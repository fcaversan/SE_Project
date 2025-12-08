"""Unit tests for HomeScreenPresenter."""

import pytest
from datetime import datetime, timedelta
from presenters.home_screen_presenter import HomeScreenPresenter
from models.vehicle_state import VehicleState
from models.user_profile import UserProfile
from models.enums import UnitSystem, TempUnit, LockStatus


@pytest.fixture
def metric_profile():
    """Create metric user profile."""
    return UserProfile(
        user_id="test",
        unit_system=UnitSystem.METRIC,
        temp_unit=TempUnit.CELSIUS
    )


@pytest.fixture
def imperial_profile():
    """Create imperial user profile."""
    return UserProfile(
        user_id="test",
        unit_system=UnitSystem.IMPERIAL,
        temp_unit=TempUnit.FAHRENHEIT
    )


@pytest.fixture
def sample_vehicle_state():
    """Create sample vehicle state."""
    return VehicleState(
        battery_soc=82.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now() - timedelta(seconds=30)
    )


def test_format_battery_percentage(metric_profile, sample_vehicle_state):
    """Test battery percentage formatting."""
    presenter = HomeScreenPresenter(metric_profile)
    result = presenter.format_battery_percentage(sample_vehicle_state)
    assert result == "82%"


def test_format_range_metric(metric_profile, sample_vehicle_state):
    """Test range formatting with metric units."""
    presenter = HomeScreenPresenter(metric_profile)
    result = presenter.format_range(sample_vehicle_state)
    assert result == "350 km"


def test_format_range_imperial(imperial_profile, sample_vehicle_state):
    """Test range formatting with imperial units."""
    presenter = HomeScreenPresenter(imperial_profile)
    result = presenter.format_range(sample_vehicle_state)
    assert "mi" in result
    assert "217" in result  # 350 km ≈ 217 miles


def test_format_temperature_celsius(metric_profile, sample_vehicle_state):
    """Test temperature formatting with Celsius."""
    presenter = HomeScreenPresenter(metric_profile)
    result = presenter.format_temperature(sample_vehicle_state)
    assert result == "22°C"


def test_format_temperature_fahrenheit(imperial_profile, sample_vehicle_state):
    """Test temperature formatting with Fahrenheit."""
    presenter = HomeScreenPresenter(imperial_profile)
    result = presenter.format_temperature(sample_vehicle_state)
    assert "°F" in result
    assert "72" in result  # 22°C ≈ 72°F


def test_format_lock_status_locked(metric_profile, sample_vehicle_state):
    """Test lock status formatting when locked."""
    presenter = HomeScreenPresenter(metric_profile)
    result = presenter.format_lock_status(sample_vehicle_state)
    assert result == "Locked"


def test_format_lock_status_unlocked(metric_profile):
    """Test lock status formatting when unlocked."""
    presenter = HomeScreenPresenter(metric_profile)
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.UNLOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now()
    )
    result = presenter.format_lock_status(state)
    assert result == "Unlocked"


def test_format_climate_status_off(metric_profile, sample_vehicle_state):
    """Test climate status formatting when off."""
    presenter = HomeScreenPresenter(metric_profile)
    result = presenter.format_climate_status(sample_vehicle_state)
    assert result == "Climate Off"


def test_format_climate_status_on(metric_profile):
    """Test climate status formatting when on."""
    presenter = HomeScreenPresenter(metric_profile)
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=True,
        last_updated=datetime.now()
    )
    result = presenter.format_climate_status(state)
    assert result == "Climate On"


def test_format_last_updated_seconds(metric_profile):
    """Test last updated formatting for recent update (seconds)."""
    presenter = HomeScreenPresenter(metric_profile)
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now() - timedelta(seconds=30)
    )
    result = presenter.format_last_updated(state)
    assert "s ago" in result


def test_format_last_updated_minutes(metric_profile):
    """Test last updated formatting for minutes."""
    presenter = HomeScreenPresenter(metric_profile)
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now() - timedelta(minutes=5)
    )
    result = presenter.format_last_updated(state)
    assert "m ago" in result


def test_format_last_updated_hours(metric_profile):
    """Test last updated formatting for hours."""
    presenter = HomeScreenPresenter(metric_profile)
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now() - timedelta(hours=2)
    )
    result = presenter.format_last_updated(state)
    assert "h ago" in result


def test_get_battery_warning_level_normal(metric_profile):
    """Test battery warning level for normal battery."""
    presenter = HomeScreenPresenter(metric_profile)
    state = VehicleState(
        battery_soc=50.0,
        estimated_range_km=200.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now()
    )
    result = presenter.get_battery_warning_level(state)
    assert result == "normal"


def test_get_battery_warning_level_low(metric_profile):
    """Test battery warning level for low battery."""
    presenter = HomeScreenPresenter(metric_profile)
    state = VehicleState(
        battery_soc=15.0,
        estimated_range_km=60.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now()
    )
    result = presenter.get_battery_warning_level(state)
    assert result == "low"


def test_get_battery_warning_level_critical(metric_profile):
    """Test battery warning level for critical battery."""
    presenter = HomeScreenPresenter(metric_profile)
    state = VehicleState(
        battery_soc=3.0,
        estimated_range_km=12.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now()
    )
    result = presenter.get_battery_warning_level(state)
    assert result == "critical"


def test_should_show_unlock_warning_false(metric_profile, sample_vehicle_state):
    """Test unlock warning check when locked."""
    presenter = HomeScreenPresenter(metric_profile)
    result = presenter.should_show_unlock_warning(sample_vehicle_state)
    assert result is False


def test_should_show_unlock_warning_true(metric_profile):
    """Test unlock warning check when unlocked too long."""
    presenter = HomeScreenPresenter(metric_profile)
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.UNLOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now(),
        lock_timestamp=datetime.now() - timedelta(minutes=15)
    )
    result = presenter.should_show_unlock_warning(state)
    assert result is True


def test_km_to_miles_conversion(metric_profile):
    """Test kilometer to miles conversion."""
    presenter = HomeScreenPresenter(metric_profile)
    result = presenter._km_to_miles(100.0)
    assert 62.0 < result < 62.2  # 100 km ≈ 62.14 miles


def test_celsius_to_fahrenheit_conversion(metric_profile):
    """Test Celsius to Fahrenheit conversion."""
    presenter = HomeScreenPresenter(metric_profile)
    result = presenter._celsius_to_fahrenheit(0.0)
    assert result == 32.0
    
    result = presenter._celsius_to_fahrenheit(100.0)
    assert result == 212.0
