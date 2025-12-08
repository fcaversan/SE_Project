"""
Integration tests for advanced climate control API endpoints.

Tests heated seats, heated steering wheel, and defrost controls.
"""

import pytest
from app import app
from models import VehicleState
from models.climate_settings import ClimateSettings
from models.enums import SeatHeatLevel, LockStatus


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    
    # Reset remote_command_service to ensure clean state
    import app as app_module
    app_module.remote_command_service = None
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def vehicle_state():
    """Create a default vehicle state for testing."""
    from datetime import datetime
    return VehicleState(
        battery_soc=80.0,
        estimated_range_km=250.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=20.0,
        climate_on=False,
        last_updated=datetime.now(),
        is_plugged_in=True
    )


def test_set_seat_heat_driver(client, vehicle_state):
    """Test setting driver seat heat level."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/seat-heat', json={
        'seat': 'front_left',
        'level': 'high'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'command_id' in data


def test_set_seat_heat_passenger(client, vehicle_state):
    """Test setting passenger seat heat level."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/seat-heat', json={
        'seat': 'front_right',
        'level': 'medium'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_set_seat_heat_rear(client, vehicle_state):
    """Test setting rear seat heat level."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/seat-heat', json={
        'seat': 'rear',
        'level': 'low'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_set_seat_heat_off(client, vehicle_state):
    """Test turning off seat heat."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/seat-heat', json={
        'seat': 'front_left',
        'level': 'off'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_set_seat_heat_invalid_seat(client, vehicle_state):
    """Test invalid seat position."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/seat-heat', json={
        'seat': 'invalid_seat',
        'level': 'high'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Invalid seat position' in data['error']


def test_set_seat_heat_invalid_level(client, vehicle_state):
    """Test invalid heat level."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/seat-heat', json={
        'seat': 'front_left',
        'level': 'super_hot'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Invalid heat level' in data['error']


def test_steering_heat_on(client, vehicle_state):
    """Test turning on heated steering wheel."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/steering-heat', json={
        'enabled': True
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'command_id' in data


def test_steering_heat_off(client, vehicle_state):
    """Test turning off heated steering wheel."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/steering-heat', json={
        'enabled': False
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_front_defrost_on(client, vehicle_state):
    """Test turning on front defrost."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/defrost', json={
        'position': 'front',
        'enabled': True
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'command_id' in data


def test_front_defrost_off(client, vehicle_state):
    """Test turning off front defrost."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/defrost', json={
        'position': 'front',
        'enabled': False
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_rear_defrost_on(client, vehicle_state):
    """Test turning on rear defrost."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/defrost', json={
        'position': 'rear',
        'enabled': True
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_rear_defrost_off(client, vehicle_state):
    """Test turning off rear defrost."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/defrost', json={
        'position': 'rear',
        'enabled': False
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_defrost_invalid_position(client, vehicle_state):
    """Test invalid defrost position."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    response = client.post('/api/vehicle/defrost', json={
        'position': 'side',
        'enabled': True
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Invalid position' in data['error']


def test_full_advanced_climate_sequence(client, vehicle_state):
    """Test complete sequence of advanced climate features."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    # Set driver seat to high
    response = client.post('/api/vehicle/seat-heat', json={
        'seat': 'front_left',
        'level': 'high'
    })
    assert response.status_code == 200
    
    # Set passenger seat to medium
    response = client.post('/api/vehicle/seat-heat', json={
        'seat': 'front_right',
        'level': 'medium'
    })
    assert response.status_code == 200
    
    # Turn on steering heat
    response = client.post('/api/vehicle/steering-heat', json={
        'enabled': True
    })
    assert response.status_code == 200
    
    # Turn on front defrost
    response = client.post('/api/vehicle/defrost', json={
        'position': 'front',
        'enabled': True
    })
    assert response.status_code == 200
    
    # Turn on rear defrost
    response = client.post('/api/vehicle/defrost', json={
        'position': 'rear',
        'enabled': True
    })
    assert response.status_code == 200
    
    # Verify state
    climate = service.vehicle_state.climate_settings
    assert climate.front_left_seat_heat == SeatHeatLevel.HIGH
    assert climate.front_right_seat_heat == SeatHeatLevel.MEDIUM
    assert climate.steering_wheel_heat is True
    assert climate.front_defrost is True
    assert climate.rear_defrost is True
