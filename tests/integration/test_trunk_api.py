"""
Integration tests for trunk/frunk API endpoints.

Tests Phase 5 (Trunk & Locate) user story functionality:
- Opening rear trunk remotely
- Opening front trunk (frunk) remotely
- Safety checks (prevent opening while moving)
- Status display
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
        trunk_status=TrunkStatus(
            front_trunk_open=False,
            rear_trunk_open=False
        ),
        speed_mph=0.0
    )
    
    return service.vehicle_state


def test_open_trunk_success(client, vehicle_state):
    """Test successfully opening rear trunk."""
    response = client.post('/api/vehicle/trunk/open')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'command_id' in data


def test_open_trunk_while_moving(client, vehicle_state):
    """Test rejection when trying to open trunk while moving."""
    # Set vehicle speed to 30 mph
    vehicle_state.speed_mph = 30.0
    
    response = client.post('/api/vehicle/trunk/open')
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'moving' in data['error'].lower()


def test_open_frunk_success(client, vehicle_state):
    """Test successfully opening front trunk."""
    response = client.post('/api/vehicle/frunk/open')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'command_id' in data


def test_open_frunk_while_moving(client, vehicle_state):
    """Test rejection when trying to open frunk while moving."""
    # Set vehicle speed to 15 mph
    vehicle_state.speed_mph = 15.0
    
    response = client.post('/api/vehicle/frunk/open')
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'moving' in data['error'].lower()


def test_trunk_status_in_vehicle_state(client, vehicle_state):
    """Test trunk status is included in vehicle state response."""
    response = client.get('/api/vehicle/status')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'trunk_status' in data['data']
    assert 'front_trunk_open' in data['data']['trunk_status']
    assert 'rear_trunk_open' in data['data']['trunk_status']


def test_trunk_command_sent(client, vehicle_state):
    """Test trunk command can be sent."""
    response = client.post('/api/vehicle/trunk/open')
    assert response.status_code == 200
    assert 'command_id' in response.get_json()


def test_frunk_command_sent(client, vehicle_state):
    """Test frunk command can be sent."""
    response = client.post('/api/vehicle/frunk/open')
    assert response.status_code == 200
    assert 'command_id' in response.get_json()


def test_full_trunk_sequence(client, vehicle_state):
    """Test complete trunk/frunk commands can be sent."""
    # Open rear trunk
    trunk_response = client.post('/api/vehicle/trunk/open')
    assert trunk_response.status_code == 200
    trunk_command_id = trunk_response.get_json()['command_id']
    
    # Open front trunk
    frunk_response = client.post('/api/vehicle/frunk/open')
    assert frunk_response.status_code == 200
    frunk_command_id = frunk_response.get_json()['command_id']
    
    # Commands should have different IDs
    assert trunk_command_id != frunk_command_id
