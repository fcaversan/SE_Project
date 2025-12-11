"""
Destination data model for navigation.

Represents a location/destination for trip planning.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Destination:
    """
    Represents a destination for navigation.
    
    Attributes:
        name: Human-readable name of the location
        address: Full street address
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        place_id: Optional external place ID (e.g., Google Places ID)
    """
    name: str
    address: str
    latitude: float
    longitude: float
    place_id: Optional[str] = None
    
    def __post_init__(self):
        """Validate coordinates."""
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'place_id': self.place_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Destination':
        """Create Destination from dictionary."""
        return cls(
            name=data['name'],
            address=data['address'],
            latitude=data['latitude'],
            longitude=data['longitude'],
            place_id=data.get('place_id')
        )
