"""
User Preferences Service
Handles storage and management of user preferences.
"""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from models.user_preferences import UserPreferences, UserProfile, NotificationPreferences, DisplayPreferences, VehiclePreferences


class PreferencesService:
    """Service for managing user preferences."""
    
    def __init__(self, storage_path: str = 'data'):
        """
        Initialize preferences service.
        
        Args:
            storage_path: Directory path for storing preferences
        """
        self.storage_path = storage_path
        self.preferences_file = os.path.join(storage_path, 'user_preferences.json')
        self._ensure_storage_exists()
        self._current_preferences: Optional[UserPreferences] = None
    
    def _ensure_storage_exists(self) -> None:
        """Ensure storage directory and file exist."""
        os.makedirs(self.storage_path, exist_ok=True)
        if not os.path.exists(self.preferences_file):
            # Create default preferences
            default_prefs = UserPreferences(user_id='default')
            self._save_to_file(default_prefs)
    
    def _save_to_file(self, preferences: UserPreferences) -> None:
        """Save preferences to file."""
        with open(self.preferences_file, 'w') as f:
            json.dump(preferences.to_dict(), f, indent=2)
    
    def _load_from_file(self) -> UserPreferences:
        """Load preferences from file."""
        try:
            with open(self.preferences_file, 'r') as f:
                data = json.load(f)
                return UserPreferences.from_dict(data)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default preferences if file doesn't exist or is invalid
            return UserPreferences(user_id='default')
    
    def get_preferences(self, user_id: str = 'default') -> UserPreferences:
        """
        Get user preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            UserPreferences object
        """
        if self._current_preferences is None:
            self._current_preferences = self._load_from_file()
        return self._current_preferences
    
    def update_preferences(self, user_id: str, updates: Dict[str, Any]) -> UserPreferences:
        """
        Update user preferences.
        
        Args:
            user_id: User identifier
            updates: Dictionary with preference updates
            
        Returns:
            Updated UserPreferences object
        """
        preferences = self.get_preferences(user_id)
        preferences.update_from_dict(updates)
        preferences.updated_at = datetime.now()
        self._save_to_file(preferences)
        self._current_preferences = preferences
        return preferences
    
    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        """
        Update user profile.
        
        Args:
            user_id: User identifier
            profile_data: Profile information
            
        Returns:
            Updated UserProfile object
        """
        preferences = self.get_preferences(user_id)
        preferences.profile = UserProfile.from_dict(profile_data)
        preferences.updated_at = datetime.now()
        self._save_to_file(preferences)
        self._current_preferences = preferences
        return preferences.profile
    
    def update_notifications(self, user_id: str, notification_data: Dict[str, Any]) -> NotificationPreferences:
        """
        Update notification preferences.
        
        Args:
            user_id: User identifier
            notification_data: Notification settings
            
        Returns:
            Updated NotificationPreferences object
        """
        preferences = self.get_preferences(user_id)
        preferences.notifications = NotificationPreferences.from_dict(notification_data)
        preferences.updated_at = datetime.now()
        self._save_to_file(preferences)
        self._current_preferences = preferences
        return preferences.notifications
    
    def update_display(self, user_id: str, display_data: Dict[str, Any]) -> DisplayPreferences:
        """
        Update display preferences.
        
        Args:
            user_id: User identifier
            display_data: Display settings
            
        Returns:
            Updated DisplayPreferences object
        """
        preferences = self.get_preferences(user_id)
        preferences.display = DisplayPreferences.from_dict(display_data)
        preferences.updated_at = datetime.now()
        self._save_to_file(preferences)
        self._current_preferences = preferences
        return preferences.display
    
    def update_vehicle(self, user_id: str, vehicle_data: Dict[str, Any]) -> VehiclePreferences:
        """
        Update vehicle preferences.
        
        Args:
            user_id: User identifier
            vehicle_data: Vehicle settings
            
        Returns:
            Updated VehiclePreferences object
        """
        preferences = self.get_preferences(user_id)
        preferences.vehicle = VehiclePreferences.from_dict(vehicle_data)
        preferences.updated_at = datetime.now()
        self._save_to_file(preferences)
        self._current_preferences = preferences
        return preferences.vehicle
    
    def reset_to_defaults(self, user_id: str) -> UserPreferences:
        """
        Reset preferences to defaults.
        
        Args:
            user_id: User identifier
            
        Returns:
            Default UserPreferences object
        """
        default_prefs = UserPreferences(user_id=user_id)
        self._save_to_file(default_prefs)
        self._current_preferences = default_prefs
        return default_prefs
    
    def export_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Export preferences as dictionary.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with all preferences
        """
        preferences = self.get_preferences(user_id)
        return preferences.to_dict()
    
    def import_preferences(self, user_id: str, data: Dict[str, Any]) -> UserPreferences:
        """
        Import preferences from dictionary.
        
        Args:
            user_id: User identifier
            data: Preferences data
            
        Returns:
            Imported UserPreferences object
        """
        preferences = UserPreferences.from_dict(data)
        preferences.user_id = user_id
        preferences.updated_at = datetime.now()
        self._save_to_file(preferences)
        self._current_preferences = preferences
        return preferences
    
    # Convenience methods for common settings
    
    def get_distance_unit(self, user_id: str = 'default') -> str:
        """Get preferred distance unit."""
        return self.get_preferences(user_id).display.distance_unit
    
    def get_temperature_unit(self, user_id: str = 'default') -> str:
        """Get preferred temperature unit."""
        return self.get_preferences(user_id).display.temperature_unit
    
    def get_theme(self, user_id: str = 'default') -> str:
        """Get preferred theme."""
        return self.get_preferences(user_id).display.theme
    
    def get_default_charging_limit(self, user_id: str = 'default') -> int:
        """Get default charging limit."""
        return self.get_preferences(user_id).vehicle.default_charging_limit
    
    def is_notification_enabled(self, user_id: str, notification_type: str) -> bool:
        """
        Check if a notification type is enabled.
        
        Args:
            user_id: User identifier
            notification_type: Type of notification
            
        Returns:
            True if enabled
        """
        prefs = self.get_preferences(user_id)
        return getattr(prefs.notifications, notification_type, False)
