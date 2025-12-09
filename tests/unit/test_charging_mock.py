"""
Unit tests for ChargingMockService.
"""

import os
import shutil
import tempfile
import time
import pytest
from datetime import datetime
from unittest.mock import patch

from models.vehicle_state import VehicleState
from models.charging_schedule import ChargingSchedule
from mocks.charging_mock import ChargingMockService


class TestChargingMockService:
    """Tests for ChargingMockService."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test data."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    @pytest.fixture
    def vehicle_state(self):
        """Create a test vehicle state."""
        from models.enums import LockStatus
        from datetime import datetime
        return VehicleState(
            battery_soc=50.0,
            estimated_range_km=250.0,
            lock_status=LockStatus.LOCKED,
            cabin_temp_celsius=22.0,
            climate_on=False,
            last_updated=datetime.now(),
            is_plugged_in=True
        )
    
    @pytest.fixture
    def charging_service(self, vehicle_state, temp_dir):
        """Create a ChargingMockService instance."""
        return ChargingMockService(
            vehicle_state=vehicle_state,
            data_dir=temp_dir,
            battery_capacity_kwh=82.0,
            max_charging_rate_kw=250.0
        )
    
    def test_initial_state(self, charging_service):
        """Test initial state of service."""
        assert charging_service.current_session is None
        assert charging_service.get_charge_limit() == 80  # Default
        assert charging_service.get_schedules() == []
        assert charging_service.get_charging_history() == []
    
    def test_start_charging_success(self, charging_service):
        """Test starting a charging session successfully."""
        session = charging_service.start_charging(target_soc=80)
        
        assert session is not None
        assert session.is_active
        assert session.start_soc == 50.0
        assert session.target_soc == 80
        # Current SoC should be close to start (thread may have started charging)
        assert 50.0 <= session.current_soc <= 51.0
        assert session.charging_rate_kw > 0
        assert session.voltage > 0
        assert session.amperage > 0
        assert session.location in ChargingMockService.CHARGING_LOCATIONS
        
        # Clean up
        charging_service.stop_charging()
    
    def test_start_charging_not_plugged_in(self, charging_service, vehicle_state):
        """Test starting charging when not plugged in fails."""
        vehicle_state.is_plugged_in = False
        
        with pytest.raises(ValueError, match="must be plugged in"):
            charging_service.start_charging(target_soc=80)
    
    def test_start_charging_already_charging(self, charging_service):
        """Test starting charging when already charging fails."""
        charging_service.start_charging(target_soc=80)
        
        with pytest.raises(ValueError, match="already active"):
            charging_service.start_charging(target_soc=90)
        
        # Clean up
        charging_service.stop_charging()
    
    def test_start_charging_invalid_target(self, charging_service):
        """Test starting charging with invalid target SoC."""
        with pytest.raises(ValueError, match="must be between 1 and 100"):
            charging_service.start_charging(target_soc=0)
        
        with pytest.raises(ValueError, match="must be between 1 and 100"):
            charging_service.start_charging(target_soc=101)
    
    def test_start_charging_target_below_current(self, charging_service):
        """Test starting charging with target below current SoC."""
        with pytest.raises(ValueError, match="must be greater than current SoC"):
            charging_service.start_charging(target_soc=40)  # Current is 50
    
    def test_stop_charging_success(self, charging_service):
        """Test stopping a charging session."""
        charging_service.start_charging(target_soc=80)
        time.sleep(0.1)  # Let it charge briefly
        
        session = charging_service.stop_charging()
        
        assert session is not None
        assert not session.is_active
        assert session.end_time is not None
        assert charging_service.current_session is None
    
    def test_stop_charging_no_session(self, charging_service):
        """Test stopping when no active session fails."""
        with pytest.raises(ValueError, match="No active charging session"):
            charging_service.stop_charging()
    
    def test_get_current_session(self, charging_service):
        """Test getting current charging session."""
        assert charging_service.get_current_session() is None
        
        charging_service.start_charging(target_soc=80)
        session = charging_service.get_current_session()
        
        assert session is not None
        assert session.is_active
        
        # Clean up
        charging_service.stop_charging()
    
    def test_charging_simulation_progress(self, charging_service, vehicle_state):
        """Test that charging simulation increases SoC."""
        initial_soc = vehicle_state.battery_soc
        charging_service.start_charging(target_soc=80)
        
        time.sleep(2.0)  # Let it charge for 2 seconds
        
        session = charging_service.get_current_session()
        assert vehicle_state.battery_soc > initial_soc
        assert session.current_soc > initial_soc
        assert session.energy_added_kwh > 0
        assert session.cost > 0
        
        # Clean up
        charging_service.stop_charging()
    
    def test_charging_auto_stops_at_target(self, charging_service, vehicle_state):
        """Test that charging stops automatically at target SoC."""
        vehicle_state.battery_soc = 79.8  # Very close to target
        charging_service.start_charging(target_soc=80)
        
        # Wait for auto-stop (should happen quickly at this SoC)
        time.sleep(5.0)
        
        assert charging_service.current_session is None  # Auto-stopped
        assert vehicle_state.battery_soc >= 80
    
    def test_charging_rate_calculation(self, charging_service):
        """Test charging rate taper at high SoC."""
        max_rate = 250.0
        
        # Low SoC - full speed
        rate_10 = charging_service._calculate_charging_rate(10, max_rate)
        assert rate_10 == max_rate
        
        # Mid SoC - slight reduction
        rate_50 = charging_service._calculate_charging_rate(50, max_rate)
        assert rate_50 == max_rate * 0.95
        
        # High SoC - significant taper
        rate_85 = charging_service._calculate_charging_rate(85, max_rate)
        assert rate_85 == max_rate * 0.6
        
        # Very high SoC - very slow
        rate_95 = charging_service._calculate_charging_rate(95, max_rate)
        assert rate_95 == max_rate * 0.3
    
    def test_get_charge_limit(self, charging_service):
        """Test getting charge limit."""
        limit = charging_service.get_charge_limit()
        assert limit == 80  # Default
    
    def test_set_charge_limit_success(self, charging_service):
        """Test setting charge limit."""
        new_limit = charging_service.set_charge_limit(90)
        assert new_limit == 90
        assert charging_service.get_charge_limit() == 90
    
    def test_set_charge_limit_invalid(self, charging_service):
        """Test setting invalid charge limit."""
        with pytest.raises(ValueError, match="must be between 1 and 100"):
            charging_service.set_charge_limit(0)
        
        with pytest.raises(ValueError, match="must be between 1 and 100"):
            charging_service.set_charge_limit(101)
    
    def test_set_charge_limit_updates_active_session(self, charging_service):
        """Test setting charge limit updates active session."""
        charging_service.start_charging(target_soc=80)
        charging_service.set_charge_limit(90)
        
        session = charging_service.get_current_session()
        assert session.target_soc == 90
        
        # Clean up
        charging_service.stop_charging()
    
    def test_charging_history_empty(self, charging_service):
        """Test getting charging history when empty."""
        history = charging_service.get_charging_history()
        assert history == []
    
    def test_charging_history_after_session(self, charging_service):
        """Test charging history saves completed sessions."""
        charging_service.start_charging(target_soc=80)
        time.sleep(0.5)
        charging_service.stop_charging()
        
        history = charging_service.get_charging_history()
        assert len(history) == 1
        assert not history[0].is_active
        assert history[0].end_time is not None
    
    def test_charging_history_limit(self, charging_service):
        """Test charging history respects limit parameter."""
        # Create multiple sessions
        for _ in range(3):
            charging_service.start_charging(target_soc=80)
            time.sleep(0.2)
            charging_service.stop_charging()
        
        history = charging_service.get_charging_history(limit=2)
        assert len(history) == 2
    
    def test_get_schedules_empty(self, charging_service):
        """Test getting schedules when empty."""
        schedules = charging_service.get_schedules()
        assert schedules == []
    
    def test_create_schedule(self, charging_service):
        """Test creating a charging schedule."""
        schedule = ChargingSchedule(
            name="Weeknight Charging",
            days_of_week=[0, 1, 2, 3, 4],
            start_time="22:00",
            target_soc=80
        )
        
        created = charging_service.create_schedule(schedule)
        assert created == schedule
        
        schedules = charging_service.get_schedules()
        assert len(schedules) == 1
        assert schedules[0].name == "Weeknight Charging"
    
    def test_update_schedule(self, charging_service):
        """Test updating a charging schedule."""
        schedule = ChargingSchedule(
            name="Test Schedule",
            days_of_week=[0, 1],
            start_time="22:00",
            target_soc=80
        )
        charging_service.create_schedule(schedule)
        
        # Update schedule
        schedule.target_soc = 90
        updated = charging_service.update_schedule(schedule)
        
        assert updated.target_soc == 90
        schedules = charging_service.get_schedules()
        assert schedules[0].target_soc == 90
    
    def test_update_schedule_not_found(self, charging_service):
        """Test updating non-existent schedule fails."""
        schedule = ChargingSchedule(
            name="Test",
            days_of_week=[0],
            start_time="22:00",
            target_soc=80
        )
        
        with pytest.raises(ValueError, match="Schedule not found"):
            charging_service.update_schedule(schedule)
    
    def test_delete_schedule(self, charging_service):
        """Test deleting a charging schedule."""
        schedule = ChargingSchedule(
            name="Test Schedule",
            days_of_week=[0, 1],
            start_time="22:00",
            target_soc=80
        )
        charging_service.create_schedule(schedule)
        
        result = charging_service.delete_schedule(schedule.schedule_id)
        assert result is True
        assert len(charging_service.get_schedules()) == 0
    
    def test_delete_schedule_not_found(self, charging_service):
        """Test deleting non-existent schedule returns False."""
        result = charging_service.delete_schedule("nonexistent-id")
        assert result is False
    
    def test_get_nearby_stations(self, charging_service):
        """Test getting nearby charging stations."""
        stations = charging_service.get_nearby_stations()
        
        assert len(stations) > 0
        assert all(s.distance_km <= 10.0 for s in stations)
        # Should be sorted by distance
        distances = [s.distance_km for s in stations]
        assert distances == sorted(distances)
    
    def test_get_nearby_stations_distance_filter(self, charging_service):
        """Test filtering stations by distance."""
        stations = charging_service.get_nearby_stations(max_distance_km=2.0)
        
        assert all(s.distance_km <= 2.0 for s in stations)
    
    def test_get_nearby_stations_connector_filter(self, charging_service):
        """Test filtering stations by connector type."""
        stations = charging_service.get_nearby_stations(connector_filter=["tesla"])
        
        assert all("tesla" in s.connector_types for s in stations)
    
    def test_get_nearby_stations_power_filter(self, charging_service):
        """Test filtering stations by power level."""
        stations = charging_service.get_nearby_stations(power_filter=150)
        
        assert all(s.max_power_kw() >= 150 for s in stations)
    
    def test_get_nearby_stations_combined_filters(self, charging_service):
        """Test combining multiple station filters."""
        stations = charging_service.get_nearby_stations(
            max_distance_km=3.0,
            connector_filter=["ccs"],
            power_filter=100
        )
        
        for station in stations:
            assert station.distance_km <= 3.0
            assert "ccs" in station.connector_types
            assert station.max_power_kw() >= 100
    
    def test_persistence_charge_limit(self, charging_service, vehicle_state, temp_dir):
        """Test charge limit persists across instances."""
        charging_service.set_charge_limit(85)
        
        # Create new instance with same data directory
        new_service = ChargingMockService(
            vehicle_state=vehicle_state,
            data_dir=temp_dir
        )
        
        assert new_service.get_charge_limit() == 85
    
    def test_persistence_schedules(self, charging_service, vehicle_state, temp_dir):
        """Test schedules persist across instances."""
        schedule = ChargingSchedule(
            name="Test Schedule",
            days_of_week=[0, 1],
            start_time="22:00",
            target_soc=80
        )
        charging_service.create_schedule(schedule)
        
        # Create new instance
        new_service = ChargingMockService(
            vehicle_state=vehicle_state,
            data_dir=temp_dir
        )
        
        schedules = new_service.get_schedules()
        assert len(schedules) == 1
        assert schedules[0].name == "Test Schedule"
    
    def test_persistence_sessions(self, charging_service, vehicle_state, temp_dir):
        """Test sessions persist across instances."""
        charging_service.start_charging(target_soc=80)
        time.sleep(0.5)
        charging_service.stop_charging()
        
        # Create new instance
        new_service = ChargingMockService(
            vehicle_state=vehicle_state,
            data_dir=temp_dir
        )
        
        history = new_service.get_charging_history()
        assert len(history) == 1
