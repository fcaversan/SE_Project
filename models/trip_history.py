"""
Trip history data model.

Represents a completed trip with statistics.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TripHistory:
    """
    Represents a completed trip.
    
    Attributes:
        trip_id: Unique identifier
        destination_name: Name of destination
        date: Trip date
        distance_km: Total distance traveled
        duration_minutes: Trip duration
        energy_used_kwh: Energy consumed
        avg_consumption: Average consumption (kWh/100km)
        start_soc: Starting battery percentage
        end_soc: Ending battery percentage
        charging_stops: Number of charging stops made
    """
    trip_id: str
    destination_name: str
    date: datetime
    distance_km: float
    duration_minutes: int
    energy_used_kwh: float
    avg_consumption: float
    start_soc: float
    end_soc: float
    charging_stops: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'trip_id': self.trip_id,
            'destination_name': self.destination_name,
            'date': self.date.isoformat(),
            'distance_km': self.distance_km,
            'duration_minutes': self.duration_minutes,
            'energy_used_kwh': self.energy_used_kwh,
            'avg_consumption': self.avg_consumption,
            'start_soc': self.start_soc,
            'end_soc': self.end_soc,
            'charging_stops': self.charging_stops
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TripHistory':
        """Create TripHistory from dictionary."""
        return cls(
            trip_id=data['trip_id'],
            destination_name=data['destination_name'],
            date=datetime.fromisoformat(data['date']),
            distance_km=data['distance_km'],
            duration_minutes=data['duration_minutes'],
            energy_used_kwh=data['energy_used_kwh'],
            avg_consumption=data['avg_consumption'],
            start_soc=data['start_soc'],
            end_soc=data['end_soc'],
            charging_stops=data.get('charging_stops', 0)
        )
