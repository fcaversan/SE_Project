"""
VehicleState model - represents current vehicle status.

Per UML class diagram: Home_Screen_Vehicle_Status_v3_class_diagram.puml
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from models.enums import LockStatus


@dataclass
class VehicleState:
    """
    Current state of the vehicle.
    
    Attributes:
        battery_soc: Battery state of charge (0-100%)
        estimated_range_km: Estimated range in kilometers
        lock_status: Current lock status (LOCKED/UNLOCKED)
        cabin_temp_celsius: Cabin temperature in Celsius
        climate_on: Whether HVAC is active
        last_updated: Timestamp of last data update
        lock_timestamp: Timestamp when lock status last changed
    """
    battery_soc: float
    estimated_range_km: float
    lock_status: LockStatus
    cabin_temp_celsius: float
    climate_on: bool
    last_updated: datetime
    lock_timestamp: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['lock_status'] = self.lock_status.value
        data['last_updated'] = self.last_updated.isoformat()
        if self.lock_timestamp:
            data['lock_timestamp'] = self.lock_timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VehicleState':
        """Create VehicleState from dictionary."""
        return cls(
            battery_soc=data['battery_soc'],
            estimated_range_km=data['estimated_range_km'],
            lock_status=LockStatus(data['lock_status']),
            cabin_temp_celsius=data['cabin_temp_celsius'],
            climate_on=data['climate_on'],
            last_updated=datetime.fromisoformat(data['last_updated']),
            lock_timestamp=(
                datetime.fromisoformat(data['lock_timestamp'])
                if data.get('lock_timestamp') else None
            )
        )
    
    def is_stale(self, threshold_seconds: int = 60) -> bool:
        """Check if data is stale (older than threshold)."""
        now = datetime.now()
        age_seconds = (now - self.last_updated).total_seconds()
        return age_seconds > threshold_seconds
    
    def is_low_battery(self) -> bool:
        """Check if battery is low (< 20%)."""
        return self.battery_soc < 20.0
    
    def is_critical_battery(self) -> bool:
        """Check if battery is critically low (< 5%)."""
        return self.battery_soc < 5.0
    
    def is_unlocked_too_long(self, threshold_minutes: int = 10) -> bool:
        """Check if vehicle has been unlocked for too long."""
        if self.lock_status != LockStatus.UNLOCKED or not self.lock_timestamp:
            return False
        now = datetime.now()
        minutes_unlocked = (now - self.lock_timestamp).total_seconds() / 60
        return minutes_unlocked > threshold_minutes
