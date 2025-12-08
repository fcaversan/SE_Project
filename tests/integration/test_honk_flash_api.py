"""
Integration tests for honk & flash API endpoint.

Tests Phase 5 (Trunk & Locate) locate vehicle functionality:
- Honking horn and flashing lights to locate vehicle
- Command execution success
"""

import pytest
from app import app
from models.enums import LockStatus
from datetime import datetime


@pytest.fixture
def client():
    """Flask test client."""
    app.config['TESTING'] = True
    
    # Reset remote_command_service to ensure clean state
    import app as app_module
    app_module.remote_command_service = None
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def vehicle_state(monkeypatch):
    """Mock vehicle state."""
    from app import get_remote_command_service
    from models.vehicle_state import VehicleState
    from models.climate_settings import ClimateSettings
    from models.trunk_status import TrunkStatus
    
    # Get the mock service instance
    service = get_remote_command_service()
    
    # Reset to default state
    service.vehicle_state = VehicleState(
        battery_soc=75.0,
        estimated_range_km=250.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now(),
        climate_settings=ClimateSettings(),
        trunk_status=TrunkStatus(),
        speed_mph=0.0
    )
    
    return service.vehicle_state


def test_honk_flash_success(client, vehicle_state):
    """Test successfully activating honk and flash."""
    response = client.post('/api/vehicle/honk-flash')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'command_id' in data


def test_honk_flash_command_sent(client, vehicle_state):
    """Test honk and flash command can be sent."""
    response = client.post('/api/vehicle/honk-flash')
    assert response.status_code == 200
    assert 'command_id' in response.get_json()


def test_honk_flash_preserves_state(client, vehicle_state):
    """Test honk and flash does not modify lock or trunk state."""
    response = client.post('/api/vehicle/honk-flash')
    assert response.status_code == 200
    
    # Honk and flash should not change lock status or open trunks immediately
    vehicle_response = client.get('/api/vehicle/status')
    vehicle_data = vehicle_response.get_json()['data']
    assert vehicle_data['lock_status'] == 'locked'
    assert vehicle_data['trunk_status']['front_trunk_open'] is False
    assert vehicle_data['trunk_status']['rear_trunk_open'] is False


def test_multiple_honk_flash_commands(client, vehicle_state):
    """Test multiple honk and flash commands can be sent."""
    # Send first honk and flash
    response1 = client.post('/api/vehicle/honk-flash')
    assert response1.status_code == 200
    command_id1 = response1.get_json()['command_id']
    
    # Send second honk and flash
    response2 = client.post('/api/vehicle/honk-flash')
    assert response2.status_code == 200
    command_id2 = response2.get_json()['command_id']
    
    # Command IDs should be different
    assert command_id1 != command_id2


def test_honk_flash_with_other_commands(client, vehicle_state):
    """Test honk and flash can be used alongside other commands."""
    # Send unlock command
    unlock_response = client.post('/api/vehicle/unlock')
    assert unlock_response.status_code == 200
    
    # Send honk and flash
    honk_response = client.post('/api/vehicle/honk-flash')
    assert honk_response.status_code == 200
    
    # Send trunk open command
    trunk_response = client.post('/api/vehicle/trunk/open')
    assert trunk_response.status_code == 200
    
    # All commands should return success
    assert unlock_response.get_json()['success'] is True
    assert honk_response.get_json()['success'] is True
    assert trunk_response.get_json()['success'] is True
