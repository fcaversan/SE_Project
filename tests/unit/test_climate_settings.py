"""
Unit tests for ClimateSettings model.

Tests temperature validation, battery drain calculation, and serialization.
"""

import pytest
from models.climate_settings import ClimateSettings
from models.enums import SeatHeatLevel


class TestClimateSettings:
    """Tests for ClimateSettings model."""
    
    def test_create_with_defaults(self):
        """Test creating settings with default values."""
        settings = ClimateSettings()
        
        assert settings.is_active is False
        assert settings.target_temp_celsius == 21.0
        assert settings.front_left_seat_heat == SeatHeatLevel.OFF
        assert settings.front_right_seat_heat == SeatHeatLevel.OFF
        assert settings.rear_seat_heat == SeatHeatLevel.OFF
        assert settings.steering_wheel_heat is False
        assert settings.front_defrost is False
        assert settings.rear_defrost is False
        assert settings.is_plugged_in is False
    
    def test_create_with_valid_temperature(self):
        """Test creating settings with custom temperature."""
        settings = ClimateSettings(target_temp_celsius=18.5)
        assert settings.target_temp_celsius == 18.5
    
    def test_temperature_validation_too_low(self):
        """Test that temperature below 15°C raises error."""
        with pytest.raises(ValueError, match="out of range"):
            ClimateSettings(target_temp_celsius=14.9)
    
    def test_temperature_validation_too_high(self):
        """Test that temperature above 28°C raises error."""
        with pytest.raises(ValueError, match="out of range"):
            ClimateSettings(target_temp_celsius=28.1)
    
    def test_temperature_validation_boundaries(self):
        """Test boundary temperatures are valid."""
        low = ClimateSettings(target_temp_celsius=15.0)
        high = ClimateSettings(target_temp_celsius=28.0)
        
        assert low.target_temp_celsius == 15.0
        assert high.target_temp_celsius == 28.0
    
    def test_set_temperature(self):
        """Test setting temperature after creation."""
        settings = ClimateSettings()
        
        settings.set_temperature(24.5)
        
        assert settings.target_temp_celsius == 24.5
    
    def test_set_temperature_validation(self):
        """Test set_temperature validates range."""
        settings = ClimateSettings()
        
        with pytest.raises(ValueError, match="out of range"):
            settings.set_temperature(30.0)
    
    def test_battery_drain_inactive_climate(self):
        """Test no battery drain when climate is off."""
        settings = ClimateSettings(is_active=False)
        
        drain = settings.estimate_battery_drain_per_10min(current_temp_celsius=20.0)
        
        assert drain == 0.0
    
    def test_battery_drain_base_hvac(self):
        """Test base HVAC drain calculation."""
        settings = ClimateSettings(
            is_active=True,
            target_temp_celsius=21.0
        )
        
        # Small temp diff = small drain
        drain_small = settings.estimate_battery_drain_per_10min(current_temp_celsius=20.0)
        assert 0 < drain_small < 1.0
        
        # Large temp diff = larger drain (up to 2% max)
        drain_large = settings.estimate_battery_drain_per_10min(current_temp_celsius=5.0)
        assert drain_large > drain_small
        assert drain_large <= 2.0
    
    def test_battery_drain_with_seat_heat(self):
        """Test additional drain from heated seats."""
        settings_no_heat = ClimateSettings(
            is_active=True,
            target_temp_celsius=21.0
        )
        
        settings_with_heat = ClimateSettings(
            is_active=True,
            target_temp_celsius=21.0,
            front_left_seat_heat=SeatHeatLevel.HIGH,
            front_right_seat_heat=SeatHeatLevel.MEDIUM
        )
        
        drain_no_heat = settings_no_heat.estimate_battery_drain_per_10min(21.0)
        drain_with_heat = settings_with_heat.estimate_battery_drain_per_10min(21.0)
        
        # Seat heat should add drain (0.2% per seat)
        assert drain_with_heat > drain_no_heat
        assert drain_with_heat >= drain_no_heat + 0.4  # Two seats
    
    def test_battery_drain_with_steering_heat(self):
        """Test additional drain from heated steering wheel."""
        settings = ClimateSettings(
            is_active=True,
            target_temp_celsius=21.0,
            steering_wheel_heat=True
        )
        
        drain = settings.estimate_battery_drain_per_10min(21.0)
        
        # Should include steering wheel drain (0.15%)
        assert drain >= 0.15
    
    def test_battery_drain_with_defrost(self):
        """Test additional drain from defrost."""
        settings = ClimateSettings(
            is_active=True,
            target_temp_celsius=21.0,
            front_defrost=True,
            rear_defrost=True
        )
        
        drain = settings.estimate_battery_drain_per_10min(21.0)
        
        # Should include defrost drain (0.3% × 2)
        assert drain >= 0.6
    
    def test_battery_drain_all_features(self):
        """Test drain with all climate features active."""
        settings = ClimateSettings(
            is_active=True,
            target_temp_celsius=24.0,
            front_left_seat_heat=SeatHeatLevel.HIGH,
            front_right_seat_heat=SeatHeatLevel.MEDIUM,
            rear_seat_heat=SeatHeatLevel.LOW,
            steering_wheel_heat=True,
            front_defrost=True,
            rear_defrost=True
        )
        
        drain = settings.estimate_battery_drain_per_10min(current_temp_celsius=10.0)
        
        # Should be substantial (base HVAC + seats + steering + defrost)
        assert drain > 2.0  # Base + all accessories
        assert isinstance(drain, float)
    
    def test_to_dict(self):
        """Test converting settings to dictionary."""
        settings = ClimateSettings(
            is_active=True,
            target_temp_celsius=22.5,
            front_left_seat_heat=SeatHeatLevel.HIGH,
            steering_wheel_heat=True,
            is_plugged_in=True
        )
        
        data = settings.to_dict()
        
        assert data['is_active'] is True
        assert data['target_temp_celsius'] == 22.5
        assert data['front_left_seat_heat'] == 'high'
        assert data['steering_wheel_heat'] is True
        assert data['is_plugged_in'] is True
    
    def test_from_dict(self):
        """Test creating settings from dictionary."""
        data = {
            'is_active': True,
            'target_temp_celsius': 19.0,
            'front_left_seat_heat': 'medium',
            'front_right_seat_heat': 'low',
            'rear_seat_heat': 'off',
            'steering_wheel_heat': False,
            'front_defrost': True,
            'rear_defrost': False,
            'is_plugged_in': True
        }
        
        settings = ClimateSettings.from_dict(data)
        
        assert settings.is_active is True
        assert settings.target_temp_celsius == 19.0
        assert settings.front_left_seat_heat == SeatHeatLevel.MEDIUM
        assert settings.front_right_seat_heat == SeatHeatLevel.LOW
        assert settings.rear_seat_heat == SeatHeatLevel.OFF
        assert settings.steering_wheel_heat is False
        assert settings.front_defrost is True
        assert settings.rear_defrost is False
        assert settings.is_plugged_in is True
    
    def test_round_trip_serialization(self):
        """Test settings can be serialized and deserialized."""
        original = ClimateSettings(
            is_active=True,
            target_temp_celsius=23.5,
            front_left_seat_heat=SeatHeatLevel.HIGH,
            rear_seat_heat=SeatHeatLevel.LOW,
            steering_wheel_heat=True,
            front_defrost=True
        )
        
        data = original.to_dict()
        restored = ClimateSettings.from_dict(data)
        
        assert restored.is_active == original.is_active
        assert restored.target_temp_celsius == original.target_temp_celsius
        assert restored.front_left_seat_heat == original.front_left_seat_heat
        assert restored.rear_seat_heat == original.rear_seat_heat
        assert restored.steering_wheel_heat == original.steering_wheel_heat
        assert restored.front_defrost == original.front_defrost
