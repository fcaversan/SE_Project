"""
UserProfile model - represents user preferences.

Per UML class diagram: Home_Screen_Vehicle_Status_v3_class_diagram.puml
"""

from dataclasses import dataclass, asdict
from models.enums import UnitSystem, TempUnit


@dataclass
class UserProfile:
    """
    User preferences and settings.
    
    Attributes:
        user_id: Unique user identifier
        unit_system: Distance unit preference (METRIC/IMPERIAL)
        temp_unit: Temperature unit preference (CELSIUS/FAHRENHEIT)
    """
    user_id: str
    unit_system: UnitSystem
    temp_unit: TempUnit
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['unit_system'] = self.unit_system.value
        data['temp_unit'] = self.temp_unit.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UserProfile':
        """Create UserProfile from dictionary."""
        return cls(
            user_id=data['user_id'],
            unit_system=UnitSystem(data['unit_system']),
            temp_unit=TempUnit(data['temp_unit'])
        )
    
    @staticmethod
    def get_default() -> 'UserProfile':
        """Get default user profile with metric units."""
        return UserProfile(
            user_id="default",
            unit_system=UnitSystem.METRIC,
            temp_unit=TempUnit.CELSIUS
        )
