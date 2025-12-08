"""
Enumeration types for Vehicle Connect application.

Defines enums per UML class diagram: Home_Screen_Vehicle_Status_v3_class_diagram.puml
"""

from enum import Enum


class UnitSystem(Enum):
    """Unit system preference for distance measurements."""
    METRIC = "metric"
    IMPERIAL = "imperial"


class TempUnit(Enum):
    """Temperature unit preference."""
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"


class LockStatus(Enum):
    """Vehicle lock state."""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
