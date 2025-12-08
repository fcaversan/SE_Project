"""
Charging Schedule data model.

Represents a scheduled charging configuration.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from uuid import uuid4


@dataclass
class ChargingSchedule:
    """
    Represents a scheduled charging configuration.
    
    Attributes:
        schedule_id: Unique identifier
        name: User-friendly name for the schedule
        enabled: Whether this schedule is active
        days_of_week: Days this schedule applies (0=Mon, 6=Sun)
        start_time: Time to start charging (HH:MM format)
        ready_by_time: Time vehicle should be ready (HH:MM format)
        target_soc: Target state of charge percentage
    
    Note: Only one of start_time or ready_by_time should be set.
    """
    name: str
    days_of_week: List[int]
    target_soc: int
    schedule_id: str = field(default_factory=lambda: str(uuid4()))
    enabled: bool = True
    start_time: Optional[str] = None
    ready_by_time: Optional[str] = None
    
    def __post_init__(self):
        """Validate schedule data."""
        # Validate name
        if not self.name or not self.name.strip():
            raise ValueError("name cannot be empty")
        
        # Validate days_of_week
        if not self.days_of_week:
            raise ValueError("days_of_week cannot be empty")
        for day in self.days_of_week:
            if not 0 <= day <= 6:
                raise ValueError("days_of_week must contain values 0-6")
        
        # Validate target_soc
        if not 1 <= self.target_soc <= 100:
            raise ValueError("target_soc must be between 1 and 100")
        
        # Validate time fields
        if self.start_time and self.ready_by_time:
            raise ValueError("Cannot set both start_time and ready_by_time")
        if not self.start_time and not self.ready_by_time:
            raise ValueError("Must set either start_time or ready_by_time")
        
        # Validate time format
        time_to_validate = self.start_time or self.ready_by_time
        if time_to_validate:
            self._validate_time_format(time_to_validate)
    
    @staticmethod
    def _validate_time_format(time_str: str):
        """Validate time string is in HH:MM format."""
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError()
            hour = int(parts[0])
            minute = int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError()
        except (ValueError, AttributeError):
            raise ValueError("Time must be in HH:MM format (00:00 to 23:59)")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'schedule_id': self.schedule_id,
            'name': self.name,
            'enabled': self.enabled,
            'days_of_week': self.days_of_week,
            'start_time': self.start_time,
            'ready_by_time': self.ready_by_time,
            'target_soc': self.target_soc
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChargingSchedule':
        """Create ChargingSchedule from dictionary."""
        return cls(
            schedule_id=data['schedule_id'],
            name=data['name'],
            enabled=data['enabled'],
            days_of_week=data['days_of_week'],
            start_time=data.get('start_time'),
            ready_by_time=data.get('ready_by_time'),
            target_soc=data['target_soc']
        )
