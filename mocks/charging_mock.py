"""
Mock implementation of charging service.

Simulates charging with realistic charging curves and station data.
"""

import os
import random
import threading
import time
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from models.charging_session import ChargingSession
from models.charging_schedule import ChargingSchedule
from models.charging_station import ChargingStation
from models.vehicle_state import VehicleState
from services.charging_service import ChargingService
from services.data_persistence import safe_read_json, atomic_write_json, ensure_directory


class ChargingMockService(ChargingService):
    """
    Mock charging service with simulation.
    
    Simulates realistic charging behavior including charging curves,
    different power levels, and time estimation.
    """
    
    # Mock charging locations
    CHARGING_LOCATIONS = [
        "Home Charger",
        "Supercharger Downtown",
        "Office Parking",
        "Supercharger Highway 101",
        "Shopping Mall Charger"
    ]
    
    def __init__(
        self,
        vehicle_state: VehicleState,
        data_dir: str = "data",
        battery_capacity_kwh: float = 82.0,
        max_charging_rate_kw: float = 250.0
    ):
        """
        Initialize mock charging service.
        
        Args:
            vehicle_state: Shared VehicleState object
            data_dir: Directory for data persistence
            battery_capacity_kwh: Battery capacity in kWh
            max_charging_rate_kw: Maximum charging rate in kW
        """
        self.vehicle_state = vehicle_state
        self.data_dir = data_dir
        self.battery_capacity_kwh = battery_capacity_kwh
        self.max_charging_rate_kw = max_charging_rate_kw
        
        # File paths
        self.sessions_file = os.path.join(data_dir, 'charging_sessions.json')
        self.schedules_file = os.path.join(data_dir, 'charging_schedules.json')
        self.preferences_file = os.path.join(data_dir, 'charging_preferences.json')
        
        # Current charging session
        self.current_session: Optional[ChargingSession] = None
        self._charging_thread: Optional[threading.Thread] = None
        self._stop_charging_flag = threading.Event()
        
        # Load persisted data
        self._load_preferences()
        self._load_schedules()
        self._load_sessions()
    
    def start_charging(self, target_soc: int) -> ChargingSession:
        """Start a charging session."""
        # Validate vehicle is plugged in
        if not self.vehicle_state.is_plugged_in:
            raise ValueError("Vehicle must be plugged in to start charging")
        
        # Check if already charging
        if self.current_session and self.current_session.is_active:
            raise ValueError("Charging session already active")
        
        # Validate target_soc
        if not 1 <= target_soc <= 100:
            raise ValueError("target_soc must be between 1 and 100")
        
        if target_soc <= self.vehicle_state.battery_soc:
            raise ValueError(f"target_soc must be greater than current SoC ({self.vehicle_state.battery_soc:.0f}%)")
        
        # Determine charging location and power
        location = random.choice(self.CHARGING_LOCATIONS)
        is_fast_charging = "Supercharger" in location
        max_rate = self.max_charging_rate_kw if is_fast_charging else 11.0  # L2 charger
        
        # Create new session
        self.current_session = ChargingSession(
            start_time=datetime.now(),
            start_soc=self.vehicle_state.battery_soc,
            current_soc=self.vehicle_state.battery_soc,
            target_soc=target_soc,
            charging_rate_kw=self._calculate_charging_rate(self.vehicle_state.battery_soc, max_rate),
            voltage=400.0 if is_fast_charging else 240.0,
            amperage=0.0,  # Will be calculated
            location=location
        )
        
        # Calculate amperage (P = V * I)
        self.current_session.amperage = (self.current_session.charging_rate_kw * 1000) / self.current_session.voltage
        
        # Start charging simulation thread
        self._stop_charging_flag.clear()
        self._charging_thread = threading.Thread(target=self._simulate_charging, daemon=True)
        self._charging_thread.start()
        
        return self.current_session
    
    def stop_charging(self) -> ChargingSession:
        """Stop the active charging session."""
        if not self.current_session or not self.current_session.is_active:
            raise ValueError("No active charging session")
        
        # Signal thread to stop
        self._stop_charging_flag.set()
        if self._charging_thread:
            self._charging_thread.join(timeout=2.0)
        
        # Mark session as complete
        self.current_session.is_active = False
        self.current_session.end_time = datetime.now()
        
        # Save to history
        self._save_session(self.current_session)
        
        completed_session = self.current_session
        self.current_session = None
        
        return completed_session
    
    def get_current_session(self) -> Optional[ChargingSession]:
        """Get the current active charging session."""
        return self.current_session
    
    def get_charging_history(self, limit: int = 10) -> List[ChargingSession]:
        """Get historical charging sessions."""
        data = safe_read_json(self.sessions_file)
        if not data or 'sessions' not in data:
            return []
        
        sessions = [ChargingSession.from_dict(s) for s in data['sessions']]
        # Sort by start time, most recent first
        sessions.sort(key=lambda s: s.start_time, reverse=True)
        return sessions[:limit]
    
    def get_charge_limit(self) -> int:
        """Get the current charge limit setting."""
        return self._charge_limit
    
    def set_charge_limit(self, limit: int) -> int:
        """Set the charge limit."""
        if not 1 <= limit <= 100:
            raise ValueError("Charge limit must be between 1 and 100")
        
        self._charge_limit = limit
        self._save_preferences()
        
        # Update current session if charging
        if self.current_session and self.current_session.is_active:
            self.current_session.target_soc = limit
        
        return self._charge_limit
    
    def get_schedules(self) -> List[ChargingSchedule]:
        """Get all charging schedules."""
        return self._schedules.copy()
    
    def create_schedule(self, schedule: ChargingSchedule) -> ChargingSchedule:
        """Create a new charging schedule."""
        self._schedules.append(schedule)
        self._save_schedules()
        return schedule
    
    def update_schedule(self, schedule: ChargingSchedule) -> ChargingSchedule:
        """Update an existing charging schedule."""
        for i, s in enumerate(self._schedules):
            if s.schedule_id == schedule.schedule_id:
                self._schedules[i] = schedule
                self._save_schedules()
                return schedule
        raise ValueError(f"Schedule not found: {schedule.schedule_id}")
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Delete a charging schedule."""
        for i, s in enumerate(self._schedules):
            if s.schedule_id == schedule_id:
                self._schedules.pop(i)
                self._save_schedules()
                return True
        return False
    
    def get_nearby_stations(
        self,
        max_distance_km: float = 10.0,
        connector_filter: Optional[List[str]] = None,
        power_filter: Optional[int] = None
    ) -> List[ChargingStation]:
        """Get nearby charging stations."""
        # Generate mock stations
        stations = self._generate_mock_stations()
        
        # Apply filters
        filtered = []
        for station in stations:
            # Distance filter
            if station.distance_km > max_distance_km:
                continue
            
            # Connector filter
            if connector_filter:
                if not any(c in station.connector_types for c in connector_filter):
                    continue
            
            # Power filter
            if power_filter:
                if station.max_power_kw() < power_filter:
                    continue
            
            filtered.append(station)
        
        # Sort by distance
        filtered.sort(key=lambda s: s.distance_km)
        return filtered
    
    def _simulate_charging(self):
        """Background thread that simulates charging progress."""
        cost_per_kwh = 0.35  # $0.35 per kWh
        
        while not self._stop_charging_flag.is_set() and self.current_session:
            # Check if target reached
            if self.vehicle_state.battery_soc >= self.current_session.target_soc:
                self._stop_charging_flag.set()
                break
            
            # Calculate current charging rate based on SoC (charging curve)
            max_rate = self.max_charging_rate_kw if "Supercharger" in self.current_session.location else 11.0
            current_rate = self._calculate_charging_rate(self.vehicle_state.battery_soc, max_rate)
            
            # Update charging rate and amperage
            self.current_session.charging_rate_kw = current_rate
            self.current_session.amperage = (current_rate * 1000) / self.current_session.voltage
            
            # Simulate 1 second of charging
            kwh_per_second = current_rate / 3600  # Convert kW to kWh per second
            soc_increase_per_second = (kwh_per_second / self.battery_capacity_kwh) * 100
            
            # Update vehicle SoC
            new_soc = min(self.current_session.target_soc, self.vehicle_state.battery_soc + soc_increase_per_second)
            self.vehicle_state.battery_soc = new_soc
            
            # Update session
            self.current_session.current_soc = new_soc
            self.current_session.energy_added_kwh += kwh_per_second
            self.current_session.cost = self.current_session.energy_added_kwh * cost_per_kwh
            
            time.sleep(1.0)  # Simulate 1 second
        
        # Auto-stop if target reached
        if self.current_session and self.vehicle_state.battery_soc >= self.current_session.target_soc:
            # Complete the session (don't call stop_charging from thread to avoid deadlock)
            self.current_session.is_active = False
            self.current_session.end_time = datetime.now()
            self._save_session(self.current_session)
            completed_session = self.current_session
            self.current_session = None
    
    def _calculate_charging_rate(self, current_soc: float, max_rate_kw: float) -> float:
        """
        Calculate charging rate based on charging curve.
        
        Simulates realistic taper at high SoC.
        """
        if current_soc < 20:
            return max_rate_kw  # Full speed at low SoC
        elif current_soc < 80:
            return max_rate_kw * 0.95  # Slight reduction
        elif current_soc < 90:
            return max_rate_kw * 0.6  # Significant taper
        else:
            return max_rate_kw * 0.3  # Very slow at high SoC
    
    def _generate_mock_stations(self) -> List[ChargingStation]:
        """Generate mock charging station data."""
        stations = [
            ChargingStation(
                name="Supercharger Downtown",
                latitude=37.7749,
                longitude=-122.4194,
                connector_types=["tesla", "ccs"],
                power_levels_kw=[150, 250],
                total_stalls=12,
                available_stalls=random.randint(6, 12),
                cost_per_kwh=0.35,
                distance_km=0.5
            ),
            ChargingStation(
                name="DC Fast Charger Main St",
                latitude=37.7750,
                longitude=-122.4200,
                connector_types=["ccs", "chademo"],
                power_levels_kw=[50, 150],
                total_stalls=4,
                available_stalls=random.randint(2, 4),
                cost_per_kwh=0.40,
                distance_km=1.2
            ),
            ChargingStation(
                name="Tesla Supercharger Highway",
                latitude=37.7760,
                longitude=-122.4100,
                connector_types=["tesla"],
                power_levels_kw=[250],
                total_stalls=16,
                available_stalls=random.randint(10, 16),
                cost_per_kwh=0.30,
                distance_km=2.8
            ),
            ChargingStation(
                name="Shopping Mall L2 Chargers",
                latitude=37.7730,
                longitude=-122.4220,
                connector_types=["j1772"],
                power_levels_kw=[11],
                total_stalls=8,
                available_stalls=random.randint(4, 8),
                cost_per_kwh=0.25,
                distance_km=3.5
            ),
            ChargingStation(
                name="Fast Charge Plaza",
                latitude=37.7800,
                longitude=-122.4150,
                connector_types=["ccs", "chademo", "tesla"],
                power_levels_kw=[50, 150, 250],
                total_stalls=20,
                available_stalls=random.randint(12, 20),
                cost_per_kwh=0.38,
                distance_km=4.2
            )
        ]
        return stations
    
    def _load_preferences(self):
        """Load charging preferences from file."""
        data = safe_read_json(self.preferences_file)
        if data:
            self._charge_limit = data.get('default_charge_limit', 80)
        else:
            self._charge_limit = 80  # Default to 80%
    
    def _save_preferences(self):
        """Save charging preferences to file."""
        ensure_directory(self.preferences_file)
        data = {
            'default_charge_limit': self._charge_limit
        }
        atomic_write_json(self.preferences_file, data)
    
    def _load_schedules(self):
        """Load charging schedules from file."""
        data = safe_read_json(self.schedules_file)
        if data and 'schedules' in data:
            self._schedules = [ChargingSchedule.from_dict(s) for s in data['schedules']]
        else:
            self._schedules = []
    
    def _save_schedules(self):
        """Save charging schedules to file."""
        ensure_directory(self.schedules_file)
        data = {
            'schedules': [s.to_dict() for s in self._schedules]
        }
        atomic_write_json(self.schedules_file, data)
    
    def _load_sessions(self):
        """Load charging session history from file."""
        # Sessions are loaded on-demand in get_charging_history()
        pass
    
    def _save_session(self, session: ChargingSession):
        """Save a completed charging session to history."""
        ensure_directory(self.sessions_file)
        
        # Load existing sessions
        data = safe_read_json(self.sessions_file)
        if not data:
            data = {'sessions': []}
        
        # Add new session
        data['sessions'].append(session.to_dict())
        
        # Keep only last 50 sessions
        if len(data['sessions']) > 50:
            data['sessions'] = data['sessions'][-50:]
        
        atomic_write_json(self.sessions_file, data)
