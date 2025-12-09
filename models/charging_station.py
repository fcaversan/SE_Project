"""
Charging Station data model.

Represents an EV charging station location.
"""

from dataclasses import dataclass, field
from typing import List
from uuid import uuid4
from models.enums import ConnectorType


@dataclass
class ChargingStation:
    """
    Represents an EV charging station.
    
    Attributes:
        station_id: Unique identifier
        name: Station name
        latitude: Geographic latitude
        longitude: Geographic longitude
        connector_types: Available connector types
        power_levels_kw: Available power levels (kW)
        available_stalls: Number of currently available charging stalls
        total_stalls: Total number of charging stalls
        is_operational: Whether station is operational
        cost_per_kwh: Cost per kilowatt-hour ($)
        distance_km: Distance from current location (km)
    """
    name: str
    latitude: float
    longitude: float
    connector_types: List[str]
    power_levels_kw: List[int]
    total_stalls: int
    cost_per_kwh: float
    station_id: str = field(default_factory=lambda: str(uuid4()))
    available_stalls: int = 0
    is_operational: bool = True
    distance_km: float = 0.0
    
    def __post_init__(self):
        """Validate station data."""
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")
        
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        
        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")
        
        if not self.connector_types:
            raise ValueError("connector_types cannot be empty")
        
        # Validate connector types
        valid_connectors = {ct.value for ct in ConnectorType}
        for connector in self.connector_types:
            if connector not in valid_connectors:
                raise ValueError(f"Invalid connector type: {connector}")
        
        if not self.power_levels_kw:
            raise ValueError("power_levels_kw cannot be empty")
        
        for power in self.power_levels_kw:
            if power <= 0:
                raise ValueError("power_levels_kw must contain positive values")
        
        if self.total_stalls < 0:
            raise ValueError("total_stalls must be non-negative")
        
        if self.available_stalls < 0 or self.available_stalls > self.total_stalls:
            raise ValueError("available_stalls must be between 0 and total_stalls")
        
        if self.cost_per_kwh < 0:
            raise ValueError("cost_per_kwh must be non-negative")
        
        if self.distance_km < 0:
            raise ValueError("distance_km must be non-negative")
    
    def availability_percentage(self) -> float:
        """Calculate availability as percentage."""
        if self.total_stalls == 0:
            return 0.0
        return (self.available_stalls / self.total_stalls) * 100
    
    def max_power_kw(self) -> int:
        """Get maximum power level available."""
        return max(self.power_levels_kw) if self.power_levels_kw else 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'station_id': self.station_id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'connector_types': self.connector_types,
            'power_levels_kw': self.power_levels_kw,
            'available_stalls': self.available_stalls,
            'total_stalls': self.total_stalls,
            'is_operational': self.is_operational,
            'cost_per_kwh': self.cost_per_kwh,
            'distance_km': self.distance_km
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChargingStation':
        """Create ChargingStation from dictionary."""
        return cls(
            station_id=data['station_id'],
            name=data['name'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            connector_types=data['connector_types'],
            power_levels_kw=data['power_levels_kw'],
            available_stalls=data['available_stalls'],
            total_stalls=data['total_stalls'],
            is_operational=data['is_operational'],
            cost_per_kwh=data['cost_per_kwh'],
            distance_km=data.get('distance_km', 0.0)
        )
