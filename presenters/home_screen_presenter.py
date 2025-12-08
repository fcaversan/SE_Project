"""
HomeScreenPresenter - Presentation logic for home screen.

Per UML class diagram: Home_Screen_Vehicle_Status_v3_class_diagram.puml
Handles data formatting and unit conversions.
"""

from models.vehicle_state import VehicleState
from models.user_profile import UserProfile
from models.enums import UnitSystem, TempUnit


class HomeScreenPresenter:
    """
    Presentation logic for home screen display.
    
    Handles formatting and unit conversions based on user preferences.
    """
    
    def __init__(self, user_profile: UserProfile):
        """
        Initialize presenter with user preferences.
        
        Args:
            user_profile: User profile with unit preferences
        """
        self.user_profile = user_profile
    
    def format_battery_percentage(self, vehicle_state: VehicleState) -> str:
        """
        Format battery percentage for display.
        
        Args:
            vehicle_state: Current vehicle state
        
        Returns:
            Formatted string (e.g., "82%")
        """
        return f"{vehicle_state.battery_soc:.0f}%"
    
    def format_range(self, vehicle_state: VehicleState) -> str:
        """
        Format range with user's preferred units.
        
        Args:
            vehicle_state: Current vehicle state
        
        Returns:
            Formatted string (e.g., "350 km" or "217 mi")
        """
        range_km = vehicle_state.estimated_range_km
        
        if self.user_profile.unit_system == UnitSystem.IMPERIAL:
            range_mi = self._km_to_miles(range_km)
            return f"{range_mi:.0f} mi"
        else:
            return f"{range_km:.0f} km"
    
    def format_temperature(self, vehicle_state: VehicleState) -> str:
        """
        Format temperature with user's preferred units.
        
        Args:
            vehicle_state: Current vehicle state
        
        Returns:
            Formatted string (e.g., "22°C" or "72°F")
        """
        temp_c = vehicle_state.cabin_temp_celsius
        
        if self.user_profile.temp_unit == TempUnit.FAHRENHEIT:
            temp_f = self._celsius_to_fahrenheit(temp_c)
            return f"{temp_f:.0f}°F"
        else:
            return f"{temp_c:.0f}°C"
    
    def format_lock_status(self, vehicle_state: VehicleState) -> str:
        """
        Format lock status for display.
        
        Args:
            vehicle_state: Current vehicle state
        
        Returns:
            Formatted string ("Locked" or "Unlocked")
        """
        return vehicle_state.lock_status.value.capitalize()
    
    def format_climate_status(self, vehicle_state: VehicleState) -> str:
        """
        Format climate control status.
        
        Args:
            vehicle_state: Current vehicle state
        
        Returns:
            Formatted string ("Climate On" or "Climate Off")
        """
        return "Climate On" if vehicle_state.climate_on else "Climate Off"
    
    def format_last_updated(self, vehicle_state: VehicleState) -> str:
        """
        Format last updated timestamp.
        
        Args:
            vehicle_state: Current vehicle state
        
        Returns:
            Formatted relative time string
        """
        from datetime import datetime
        
        now = datetime.now()
        diff = now - vehicle_state.last_updated
        seconds = int(diff.total_seconds())
        
        if seconds < 60:
            return f"{seconds}s ago"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m ago"
        else:
            hours = seconds // 3600
            return f"{hours}h ago"
    
    @staticmethod
    def _km_to_miles(km: float) -> float:
        """Convert kilometers to miles."""
        return km * 0.621371
    
    @staticmethod
    def _celsius_to_fahrenheit(celsius: float) -> float:
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9 / 5) + 32
    
    def get_battery_warning_level(self, vehicle_state: VehicleState) -> str:
        """
        Get battery warning level for UI styling.
        
        Args:
            vehicle_state: Current vehicle state
        
        Returns:
            Warning level: "normal", "low", or "critical"
        """
        if vehicle_state.is_critical_battery():
            return "critical"
        elif vehicle_state.is_low_battery():
            return "low"
        else:
            return "normal"
    
    def should_show_unlock_warning(self, vehicle_state: VehicleState) -> bool:
        """
        Determine if unlock warning should be shown.
        
        Args:
            vehicle_state: Current vehicle state
        
        Returns:
            True if warning should be displayed
        """
        return vehicle_state.is_unlocked_too_long()
