"""Unit tests for VehicleState model."""

import pytest
from datetime import datetime, timedelta
from models.vehicle_state import VehicleState
from models.enums import LockStatus


def test_vehicle_state_creation():
    """Test VehicleState instantiation."""
    now = datetime.now()
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=now
    )
    
    assert state.battery_soc == 80.0
    assert state.estimated_range_km == 350.0
    assert state.lock_status == LockStatus.LOCKED
    assert state.cabin_temp_celsius == 22.0
    assert state.climate_on is False
    assert state.last_updated == now


def test_vehicle_state_to_dict():
    """Test conversion to dictionary."""
    now = datetime.now()
    state = VehicleState(
        battery_soc=75.0,
        estimated_range_km=320.0,
        lock_status=LockStatus.UNLOCKED,
        cabin_temp_celsius=20.0,
        climate_on=True,
        last_updated=now
    )
    
    data = state.to_dict()
    
    assert data['battery_soc'] == 75.0
    assert data['estimated_range_km'] == 320.0
    assert data['lock_status'] == 'unlocked'
    assert data['cabin_temp_celsius'] == 20.0
    assert data['climate_on'] is True
    assert data['last_updated'] == now.isoformat()


def test_vehicle_state_from_dict():
    """Test creation from dictionary."""
    now = datetime.now()
    data = {
        'battery_soc': 65.0,
        'estimated_range_km': 280.0,
        'lock_status': 'locked',
        'cabin_temp_celsius': 21.0,
        'climate_on': False,
        'last_updated': now.isoformat()
    }
    
    state = VehicleState.from_dict(data)
    
    assert state.battery_soc == 65.0
    assert state.estimated_range_km == 280.0
    assert state.lock_status == LockStatus.LOCKED
    assert state.cabin_temp_celsius == 21.0
    assert state.climate_on is False
    assert state.last_updated == now


def test_is_stale_fresh_data():
    """Test stale check with fresh data."""
    now = datetime.now()
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=now
    )
    
    assert state.is_stale() is False


def test_is_stale_old_data():
    """Test stale check with old data."""
    old_time = datetime.now() - timedelta(seconds=90)
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=old_time
    )
    
    assert state.is_stale() is True


def test_is_low_battery_normal():
    """Test low battery check with normal level."""
    state = VehicleState(
        battery_soc=50.0,
        estimated_range_km=200.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now()
    )
    
    assert state.is_low_battery() is False


def test_is_low_battery_low():
    """Test low battery check with low level."""
    state = VehicleState(
        battery_soc=15.0,
        estimated_range_km=60.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now()
    )
    
    assert state.is_low_battery() is True


def test_is_critical_battery_normal():
    """Test critical battery check with normal level."""
    state = VehicleState(
        battery_soc=30.0,
        estimated_range_km=120.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now()
    )
    
    assert state.is_critical_battery() is False


def test_is_critical_battery_critical():
    """Test critical battery check with critical level."""
    state = VehicleState(
        battery_soc=3.0,
        estimated_range_km=12.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now()
    )
    
    assert state.is_critical_battery() is True


def test_is_unlocked_too_long_locked():
    """Test unlocked duration check when locked."""
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now(),
        lock_timestamp=datetime.now()
    )
    
    assert state.is_unlocked_too_long() is False


def test_is_unlocked_too_long_recent():
    """Test unlocked duration check with recent unlock."""
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.UNLOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now(),
        lock_timestamp=datetime.now() - timedelta(minutes=5)
    )
    
    assert state.is_unlocked_too_long() is False


def test_is_unlocked_too_long_prolonged():
    """Test unlocked duration check with prolonged unlock."""
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.UNLOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now(),
        lock_timestamp=datetime.now() - timedelta(minutes=15)
    )
    
    assert state.is_unlocked_too_long() is True


def test_is_unlocked_too_long_no_timestamp():
    """Test unlocked duration check without timestamp."""
    state = VehicleState(
        battery_soc=80.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.UNLOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now(),
        lock_timestamp=None
    )
    
    assert state.is_unlocked_too_long() is False
