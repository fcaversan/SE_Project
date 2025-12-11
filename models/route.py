"""
Route data model for trip planning.

Represents a planned route with charging stops.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from models.destination import Destination
from models.charging_station import ChargingStation


@dataclass
class ChargingStop:
    """
    Represents a charging stop along a route.
    
    Attributes:
        station: The charging station
        arrival_soc: Estimated SoC when arriving (percentage)
        departure_soc: Target SoC when leaving (percentage)
        charging_time_minutes: Estimated charging duration
        distance_from_start_km: Distance from route start
    """
    station: ChargingStation
    arrival_soc: float
    departure_soc: float
    charging_time_minutes: int
    distance_from_start_km: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'station': self.station.to_dict(),
            'arrival_soc': self.arrival_soc,
            'departure_soc': self.departure_soc,
            'charging_time_minutes': self.charging_time_minutes,
            'distance_from_start_km': self.distance_from_start_km
        }


@dataclass
class Route:
    """
    Represents a planned route with optional charging stops.
    
    Attributes:
        origin: Starting location
        destination: End location
        distance_km: Total route distance
        duration_minutes: Estimated travel time (without charging)
        estimated_energy_kwh: Estimated energy consumption
        charging_stops: List of required charging stops
        arrival_soc: Estimated SoC at destination (percentage)
        created_at: When this route was calculated
    """
    origin: Destination
    destination: Destination
    distance_km: float
    duration_minutes: int
    estimated_energy_kwh: float
    arrival_soc: float
    charging_stops: List[ChargingStop] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate route data."""
        if self.distance_km < 0:
            raise ValueError("distance_km must be non-negative")
        if self.duration_minutes < 0:
            raise ValueError("duration_minutes must be non-negative")
        if not 0 <= self.arrival_soc <= 100:
            raise ValueError("arrival_soc must be between 0 and 100")
    
    @property
    def total_time_with_charging_minutes(self) -> int:
        """Calculate total trip time including charging stops."""
        charging_time = sum(stop.charging_time_minutes for stop in self.charging_stops)
        return self.duration_minutes + charging_time
    
    @property
    def needs_charging(self) -> bool:
        """Check if route requires charging stops."""
        return len(self.charging_stops) > 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'origin': self.origin.to_dict(),
            'destination': self.destination.to_dict(),
            'distance_km': self.distance_km,
            'duration_minutes': self.duration_minutes,
            'estimated_energy_kwh': self.estimated_energy_kwh,
            'arrival_soc': self.arrival_soc,
            'charging_stops': [stop.to_dict() for stop in self.charging_stops],
            'total_time_with_charging_minutes': self.total_time_with_charging_minutes,
            'needs_charging': self.needs_charging,
            'created_at': self.created_at.isoformat()
        }
