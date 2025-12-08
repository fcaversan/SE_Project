"""
Climate settings model for vehicle climate control.

Represents the complete state of climate control including temperature,
heated seats, heated steering wheel, and defrost settings.
"""

from dataclasses import dataclass
from typing import Dict, Any

from models.enums import SeatHeatLevel


@dataclass
class ClimateSettings:
    """
    Complete climate control state for the vehicle.
    
    Manages temperature, heated seats/steering, and defrost settings.
    Used for both current state and command parameters.
    
    Attributes:
        is_active: Whether climate control is currently running
        target_temp_celsius: Target cabin temperature (15-28°C range)
        front_left_seat_heat: Driver seat heating level
        front_right_seat_heat: Passenger seat heating level
        rear_seat_heat: Rear seats heating level
        steering_wheel_heat: Whether steering wheel heating is active
        front_defrost: Front windshield defrost active
        rear_defrost: Rear window defrost active
        is_plugged_in: Whether vehicle is connected to charger
    """
    
    is_active: bool = False
    target_temp_celsius: float = 21.0
    front_left_seat_heat: SeatHeatLevel = SeatHeatLevel.OFF
    front_right_seat_heat: SeatHeatLevel = SeatHeatLevel.OFF
    rear_seat_heat: SeatHeatLevel = SeatHeatLevel.OFF
    steering_wheel_heat: bool = False
    front_defrost: bool = False
    rear_defrost: bool = False
    is_plugged_in: bool = False
    
    def __post_init__(self) -> None:
        """Validate temperature range after initialization."""
        if not 15.0 <= self.target_temp_celsius <= 28.0:
            raise ValueError(
                f"Temperature {self.target_temp_celsius}°C out of range (15-28°C)"
            )
    
    def set_temperature(self, temp_celsius: float) -> None:
        """
        Set target temperature with validation.
        
        Args:
            temp_celsius: Target temperature in Celsius (15-28°C)
            
        Raises:
            ValueError: If temperature is outside valid range
        """
        if not 15.0 <= temp_celsius <= 28.0:
            raise ValueError(
                f"Temperature {temp_celsius}°C out of range (15-28°C)"
            )
        self.target_temp_celsius = temp_celsius
    
    def estimate_battery_drain_per_10min(self, current_temp_celsius: float) -> float:
        """
        Estimate battery drain percentage per 10 minutes of climate operation.
        
        Drain depends on temperature differential and heated accessories.
        
        Args:
            current_temp_celsius: Current cabin temperature
            
        Returns:
            Estimated battery drain percentage (1.0 = 1%)
        """
        if not self.is_active:
            return 0.0
        
        # Base drain from HVAC based on temperature differential
        temp_diff = abs(self.target_temp_celsius - current_temp_celsius)
        base_drain = min(temp_diff * 0.15, 2.0)  # Max 2% for extreme temps
        
        # Additional drain from heated seats (0.2% per seat on non-OFF)
        seat_drain = 0.0
        if self.front_left_seat_heat != SeatHeatLevel.OFF:
            seat_drain += 0.2
        if self.front_right_seat_heat != SeatHeatLevel.OFF:
            seat_drain += 0.2
        if self.rear_seat_heat != SeatHeatLevel.OFF:
            seat_drain += 0.3  # Rear seats draw more power
        
        # Additional drain from steering wheel (0.15%)
        if self.steering_wheel_heat:
            seat_drain += 0.15
        
        # Additional drain from defrost (0.3% per defrost)
        defrost_drain = 0.0
        if self.front_defrost:
            defrost_drain += 0.3
        if self.rear_defrost:
            defrost_drain += 0.3
        
        total_drain = base_drain + seat_drain + defrost_drain
        return round(total_drain, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation with all fields
        """
        return {
            'is_active': self.is_active,
            'target_temp_celsius': self.target_temp_celsius,
            'front_left_seat_heat': self.front_left_seat_heat.value,
            'front_right_seat_heat': self.front_right_seat_heat.value,
            'rear_seat_heat': self.rear_seat_heat.value,
            'steering_wheel_heat': self.steering_wheel_heat,
            'front_defrost': self.front_defrost,
            'rear_defrost': self.rear_defrost,
            'is_plugged_in': self.is_plugged_in
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClimateSettings':
        """
        Create settings from dictionary (e.g., loaded from JSON).
        
        Args:
            data: Dictionary with climate settings fields
            
        Returns:
            ClimateSettings instance
        """
        return cls(
            is_active=data.get('is_active', False),
            target_temp_celsius=data.get('target_temp_celsius', 21.0),
            front_left_seat_heat=SeatHeatLevel(data.get('front_left_seat_heat', 'off')),
            front_right_seat_heat=SeatHeatLevel(data.get('front_right_seat_heat', 'off')),
            rear_seat_heat=SeatHeatLevel(data.get('rear_seat_heat', 'off')),
            steering_wheel_heat=data.get('steering_wheel_heat', False),
            front_defrost=data.get('front_defrost', False),
            rear_defrost=data.get('rear_defrost', False),
            is_plugged_in=data.get('is_plugged_in', False)
        )
