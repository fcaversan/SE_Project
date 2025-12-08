"""Unit tests for VehicleDataMockService."""

import pytest
from datetime import datetime
from mocks.vehicle_data_mock import VehicleDataMockService
from models.enums import LockStatus


def test_mock_service_creation():
    """Test mock service instantiation."""
    service = VehicleDataMockService(delay_seconds=0.1)
    assert service.delay_seconds == 0.1
    assert service.failure_rate == 0.0
    assert service.scenario == 'normal'


def test_get_vehicle_state_normal():
    """Test getting vehicle state with normal scenario."""
    service = VehicleDataMockService(delay_seconds=0.0, scenario='normal')
    state = service.get_vehicle_state()
    
    assert state is not None
    assert state.battery_soc > 0
    assert state.estimated_range_km > 0
    assert state.lock_status in [LockStatus.LOCKED, LockStatus.UNLOCKED]


def test_get_vehicle_state_low_battery():
    """Test getting vehicle state with low battery scenario."""
    service = VehicleDataMockService(delay_seconds=0.0, scenario='low_battery')
    state = service.get_vehicle_state()
    
    assert state.is_low_battery() is True


def test_get_vehicle_state_critical_battery():
    """Test getting vehicle state with critical battery scenario."""
    service = VehicleDataMockService(delay_seconds=0.0, scenario='critical_battery')
    state = service.get_vehicle_state()
    
    assert state.is_critical_battery() is True


def test_get_vehicle_state_unlocked():
    """Test getting vehicle state with unlocked scenario."""
    service = VehicleDataMockService(delay_seconds=0.0, scenario='unlocked')
    state = service.get_vehicle_state()
    
    assert state.lock_status == LockStatus.UNLOCKED


def test_get_vehicle_state_climate_active():
    """Test getting vehicle state with climate active scenario."""
    service = VehicleDataMockService(delay_seconds=0.0, scenario='climate_active')
    state = service.get_vehicle_state()
    
    assert state.climate_on is True


def test_refresh_data():
    """Test refreshing vehicle data."""
    service = VehicleDataMockService(delay_seconds=0.0, scenario='normal')
    state = service.refresh_data()
    
    assert state is not None
    assert isinstance(state.last_updated, datetime)


def test_set_scenario():
    """Test changing mock scenario."""
    service = VehicleDataMockService(delay_seconds=0.0, scenario='normal')
    
    state1 = service.get_vehicle_state()
    normal_soc = state1.battery_soc
    
    service.set_scenario('low_battery')
    state2 = service.get_vehicle_state()
    
    assert state2.is_low_battery() is True
    assert state2.battery_soc < normal_soc


def test_set_failure_rate():
    """Test setting failure rate."""
    service = VehicleDataMockService(delay_seconds=0.0)
    
    service.set_failure_rate(0.5)
    assert service.failure_rate == 0.5
    
    service.set_failure_rate(1.5)  # Should clamp to 1.0
    assert service.failure_rate == 1.0
    
    service.set_failure_rate(-0.5)  # Should clamp to 0.0
    assert service.failure_rate == 0.0


def test_simulated_failure():
    """Test simulated failure."""
    service = VehicleDataMockService(delay_seconds=0.0, failure_rate=1.0)
    
    with pytest.raises(Exception, match="Mock failure"):
        service.get_vehicle_state()


def test_simulated_failure_refresh():
    """Test simulated failure on refresh."""
    service = VehicleDataMockService(delay_seconds=0.0, failure_rate=1.0)
    
    with pytest.raises(Exception, match="Mock failure"):
        service.refresh_data()
