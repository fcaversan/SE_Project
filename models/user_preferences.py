"""
User Preferences Model
Represents user settings and preferences for the application.
"""

from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime


@dataclass
class NotificationPreferences:
    """Notification settings for various events."""
    charging_complete: bool = True
    charging_interrupted: bool = True
    low_battery: bool = True
    low_battery_threshold: int = 20  # Percentage
    software_updates: bool = True
    service_reminders: bool = True
    trip_updates: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'charging_complete': self.charging_complete,
            'charging_interrupted': self.charging_interrupted,
            'low_battery': self.low_battery,
            'low_battery_threshold': self.low_battery_threshold,
            'software_updates': self.software_updates,
            'service_reminders': self.service_reminders,
            'trip_updates': self.trip_updates
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationPreferences':
        """Create from dictionary."""
        return cls(
            charging_complete=data.get('charging_complete', True),
            charging_interrupted=data.get('charging_interrupted', True),
            low_battery=data.get('low_battery', True),
            low_battery_threshold=data.get('low_battery_threshold', 20),
            software_updates=data.get('software_updates', True),
            service_reminders=data.get('service_reminders', True),
            trip_updates=data.get('trip_updates', False)
        )


@dataclass
class DisplayPreferences:
    """Display and UI settings."""
    distance_unit: str = 'km'  # 'km' or 'mi'
    temperature_unit: str = 'C'  # 'C' or 'F'
    energy_unit: str = 'kWh'  # 'kWh' or 'kWh/100km' or 'mi/kWh'
    time_format: str = '24h'  # '24h' or '12h'
    theme: str = 'auto'  # 'light', 'dark', or 'auto'
    language: str = 'en'  # ISO language code
    show_range: bool = True
    show_charging_stations: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'distance_unit': self.distance_unit,
            'temperature_unit': self.temperature_unit,
            'energy_unit': self.energy_unit,
            'time_format': self.time_format,
            'theme': self.theme,
            'language': self.language,
            'show_range': self.show_range,
            'show_charging_stations': self.show_charging_stations
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DisplayPreferences':
        """Create from dictionary."""
        return cls(
            distance_unit=data.get('distance_unit', 'km'),
            temperature_unit=data.get('temperature_unit', 'C'),
            energy_unit=data.get('energy_unit', 'kWh'),
            time_format=data.get('time_format', '24h'),
            theme=data.get('theme', 'auto'),
            language=data.get('language', 'en'),
            show_range=data.get('show_range', True),
            show_charging_stations=data.get('show_charging_stations', True)
        )


@dataclass
class VehiclePreferences:
    """Vehicle-specific settings."""
    default_charging_limit: int = 80  # Percentage
    preconditioning_enabled: bool = True
    departure_time: str = '08:00'  # HH:MM format
    seat_heating_auto: bool = False
    steering_wheel_heating_auto: bool = False
    climate_auto_on: bool = True
    max_charging_current: int = 32  # Amperes
    regenerative_braking: str = 'standard'  # 'low', 'standard', 'high'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'default_charging_limit': self.default_charging_limit,
            'preconditioning_enabled': self.preconditioning_enabled,
            'departure_time': self.departure_time,
            'seat_heating_auto': self.seat_heating_auto,
            'steering_wheel_heating_auto': self.steering_wheel_heating_auto,
            'climate_auto_on': self.climate_auto_on,
            'max_charging_current': self.max_charging_current,
            'regenerative_braking': self.regenerative_braking
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VehiclePreferences':
        """Create from dictionary."""
        return cls(
            default_charging_limit=data.get('default_charging_limit', 80),
            preconditioning_enabled=data.get('preconditioning_enabled', True),
            departure_time=data.get('departure_time', '08:00'),
            seat_heating_auto=data.get('seat_heating_auto', False),
            steering_wheel_heating_auto=data.get('steering_wheel_heating_auto', False),
            climate_auto_on=data.get('climate_auto_on', True),
            max_charging_current=data.get('max_charging_current', 32),
            regenerative_braking=data.get('regenerative_braking', 'standard')
        )


@dataclass
class UserProfile:
    """User profile information."""
    name: str = ''
    email: str = ''
    phone: str = ''
    avatar_url: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'avatar_url': self.avatar_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create from dictionary."""
        return cls(
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            avatar_url=data.get('avatar_url', '')
        )


@dataclass
class UserPreferences:
    """Complete user preferences and settings."""
    user_id: str
    profile: UserProfile = field(default_factory=UserProfile)
    notifications: NotificationPreferences = field(default_factory=NotificationPreferences)
    display: DisplayPreferences = field(default_factory=DisplayPreferences)
    vehicle: VehiclePreferences = field(default_factory=VehiclePreferences)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'user_id': self.user_id,
            'profile': self.profile.to_dict(),
            'notifications': self.notifications.to_dict(),
            'display': self.display.to_dict(),
            'vehicle': self.vehicle.to_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """Create from dictionary."""
        return cls(
            user_id=data.get('user_id', 'default'),
            profile=UserProfile.from_dict(data.get('profile', {})),
            notifications=NotificationPreferences.from_dict(data.get('notifications', {})),
            display=DisplayPreferences.from_dict(data.get('display', {})),
            vehicle=VehiclePreferences.from_dict(data.get('vehicle', {})),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now()
        )
    
    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update preferences from dictionary."""
        if 'profile' in data:
            self.profile = UserProfile.from_dict(data['profile'])
        if 'notifications' in data:
            self.notifications = NotificationPreferences.from_dict(data['notifications'])
        if 'display' in data:
            self.display = DisplayPreferences.from_dict(data['display'])
        if 'vehicle' in data:
            self.vehicle = VehiclePreferences.from_dict(data['vehicle'])
        self.updated_at = datetime.now()
