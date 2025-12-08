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


class CommandType(Enum):
    """Remote command types."""
    LOCK = "lock"
    UNLOCK = "unlock"
    CLIMATE_ON = "climate_on"
    CLIMATE_OFF = "climate_off"
    SET_TEMP = "set_temp"
    SEAT_HEAT = "seat_heat"
    STEERING_HEAT = "steering_heat"
    DEFROST = "defrost"
    TRUNK_OPEN = "trunk_open"
    FRUNK_OPEN = "frunk_open"
    HONK_FLASH = "honk_flash"


class CommandStatus(Enum):
    """Remote command execution status."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ChargingStatus(Enum):
    """Vehicle charging state."""
    NOT_CHARGING = "not_charging"
    CHARGING = "charging"
    COMPLETE = "complete"
    SCHEDULED = "scheduled"
    ERROR = "error"


class ConnectorType(Enum):
    """EV charging connector types."""
    TESLA = "tesla"
    CCS = "ccs"
    CHADEMO = "chademo"
    J1772 = "j1772"


class SeatHeatLevel(Enum):
    """Heated seat temperature levels."""
    OFF = "off"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
