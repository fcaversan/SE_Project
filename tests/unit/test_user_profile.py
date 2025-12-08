"""Unit tests for UserProfile model."""

import pytest
from models.user_profile import UserProfile
from models.enums import UnitSystem, TempUnit


def test_user_profile_creation():
    """Test UserProfile instantiation."""
    profile = UserProfile(
        user_id="test_user",
        unit_system=UnitSystem.METRIC,
        temp_unit=TempUnit.CELSIUS
    )
    
    assert profile.user_id == "test_user"
    assert profile.unit_system == UnitSystem.METRIC
    assert profile.temp_unit == TempUnit.CELSIUS


def test_user_profile_to_dict():
    """Test conversion to dictionary."""
    profile = UserProfile(
        user_id="test_user",
        unit_system=UnitSystem.IMPERIAL,
        temp_unit=TempUnit.FAHRENHEIT
    )
    
    data = profile.to_dict()
    
    assert data['user_id'] == "test_user"
    assert data['unit_system'] == 'imperial'
    assert data['temp_unit'] == 'fahrenheit'


def test_user_profile_from_dict():
    """Test creation from dictionary."""
    data = {
        'user_id': "test_user",
        'unit_system': 'metric',
        'temp_unit': 'celsius'
    }
    
    profile = UserProfile.from_dict(data)
    
    assert profile.user_id == "test_user"
    assert profile.unit_system == UnitSystem.METRIC
    assert profile.temp_unit == TempUnit.CELSIUS


def test_get_default_profile():
    """Test default profile creation."""
    profile = UserProfile.get_default()
    
    assert profile.user_id == "default"
    assert profile.unit_system == UnitSystem.METRIC
    assert profile.temp_unit == TempUnit.CELSIUS


def test_profile_roundtrip():
    """Test to_dict and from_dict roundtrip."""
    original = UserProfile(
        user_id="roundtrip_test",
        unit_system=UnitSystem.IMPERIAL,
        temp_unit=TempUnit.FAHRENHEIT
    )
    
    data = original.to_dict()
    restored = UserProfile.from_dict(data)
    
    assert restored.user_id == original.user_id
    assert restored.unit_system == original.unit_system
    assert restored.temp_unit == original.temp_unit
