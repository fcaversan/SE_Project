"""
Integration tests for climate control API endpoints.

Tests climate on/off, temperature updates, battery checks, and safety validations.
"""

import pytest
from app import app
from models import VehicleState
from models.climate_settings import ClimateSettings
from models.enums import SeatHeatLevel


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
    from models.enums import LockStatus
    return VehicleState(
        battery_soc=80.0,
        estimated_range_km=250.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=20.0,
        climate_on=False,
        last_updated=datetime.now(),
        is_plugged_in=True
    )


def test_start_climate_success(client, vehicle_state, monkeypatch):
    """Test starting climate control successfully."""
    from app import get_remote_command_service
    
    # Setup mock service with test state
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    # Start climate with temperature
    response = client.post('/api/vehicle/climate', json={
        'action': 'start',
        'temperature': 22.0
    })
    
    if response.status_code != 200:
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_json()}")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'command_id' in data
    assert 'battery_drain_estimate' in data
    assert data['is_plugged_in'] is True


def test_stop_climate_success(client, vehicle_state, monkeypatch):
    """Test stopping climate control successfully."""
    from app import get_remote_command_service
    
    # Setup mock service with climate active
    service = get_remote_command_service()
    vehicle_state.climate_settings = ClimateSettings(
        is_active=True,
        target_temp_celsius=21.0,
        is_plugged_in=True
    )
    service.vehicle_state = vehicle_state
    
    # Stop climate
    response = client.post('/api/vehicle/climate', json={
        'action': 'stop'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'command_id' in data


def test_start_climate_low_battery(client, vehicle_state):
    """Test climate start is rejected when battery is too low."""
    from app import get_remote_command_service
    
    # Setup mock service with low battery
    service = get_remote_command_service()
    vehicle_state.battery_soc = 5.0
    service.vehicle_state = vehicle_state
    
    # Try to start climate
    response = client.post('/api/vehicle/climate', json={
        'action': 'start',
        'temperature': 21.0
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'Battery too low' in data['error']


def test_start_climate_invalid_temperature_low(client, vehicle_state):
    """Test climate start with temperature too low."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    # Try to start with temp below 15°C
    response = client.post('/api/vehicle/climate', json={
        'action': 'start',
        'temperature': 10.0
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'between 15' in data['error']


def test_start_climate_invalid_temperature_high(client, vehicle_state):
    """Test climate start with temperature too high."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    # Try to start with temp above 28°C
    response = client.post('/api/vehicle/climate', json={
        'action': 'start',
        'temperature': 30.0
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'between 15' in data['error']


def test_update_climate_temperature(client, vehicle_state):
    """Test updating climate temperature while running."""
    from app import get_remote_command_service
    
    # Setup mock service with climate active
    service = get_remote_command_service()
    vehicle_state.climate_settings = ClimateSettings(
        is_active=True,
        target_temp_celsius=21.0,
        is_plugged_in=True
    )
    service.vehicle_state = vehicle_state
    
    # Update temperature
    response = client.put('/api/vehicle/climate', json={
        'temperature': 24.0
    })
    
    if response.status_code != 200:
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_json()}")
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'command_id' in data
    assert 'battery_drain_estimate' in data


def test_update_climate_when_not_active(client, vehicle_state):
    """Test updating climate temperature when climate is off."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    # Try to update temperature when climate is off
    response = client.put('/api/vehicle/climate', json={
        'temperature': 22.0
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'not active' in data['error']


def test_update_climate_invalid_temperature(client, vehicle_state):
    """Test updating climate with invalid temperature."""
    from app import get_remote_command_service
    
    # Setup mock service with climate active
    service = get_remote_command_service()
    vehicle_state.climate_settings = ClimateSettings(
        is_active=True,
        target_temp_celsius=21.0,
        is_plugged_in=True
    )
    service.vehicle_state = vehicle_state
    
    # Try to update with invalid temp
    response = client.put('/api/vehicle/climate', json={
        'temperature': 35.0
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'between 15' in data['error']


def test_climate_not_plugged_in_warning(client, vehicle_state):
    """Test climate start when not plugged in (should succeed but indicate not plugged)."""
    from app import get_remote_command_service
    
    # Setup mock service not plugged in
    service = get_remote_command_service()
    vehicle_state.is_plugged_in = False
    service.vehicle_state = vehicle_state
    
    # Start climate
    response = client.post('/api/vehicle/climate', json={
        'action': 'start',
        'temperature': 21.0
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['is_plugged_in'] is False
    assert 'battery_drain_estimate' in data


def test_climate_battery_drain_calculation(client, vehicle_state):
    """Test battery drain estimate is calculated correctly."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    # Start climate at various temperatures
    for temp in [15.0, 21.0, 28.0]:
        response = client.post('/api/vehicle/climate', json={
            'action': 'start',
            'temperature': temp
        })
        
        data = response.get_json()
        assert 'battery_drain_estimate' in data
        
        # Drain should be reasonable (0.5-3%)
        # Lower at comfort temp (21°C), higher at extremes
        drain = data['battery_drain_estimate']
        assert 0.5 <= drain <= 3.0


def test_climate_start_stop_sequence(client, vehicle_state):
    """Test complete climate start-stop sequence."""
    from app import get_remote_command_service
    
    service = get_remote_command_service()
    service.vehicle_state = vehicle_state
    
    # Start climate
    response = client.post('/api/vehicle/climate', json={
        'action': 'start',
        'temperature': 22.0
    })
    assert response.status_code == 200
    assert response.get_json()['success'] is True
    
    # Verify climate is active
    assert service.vehicle_state.climate_settings is not None
    assert service.vehicle_state.climate_settings.is_active is True
    assert service.vehicle_state.climate_settings.target_temp_celsius == 22.0
    
    # Update temperature
    response = client.put('/api/vehicle/climate', json={
        'temperature': 24.0
    })
    assert response.status_code == 200
    assert response.get_json()['success'] is True
    
    # Stop climate
    response = client.post('/api/vehicle/climate', json={
        'action': 'stop'
    })
    assert response.status_code == 200
    assert response.get_json()['success'] is True
    
    # Verify climate is off
    assert service.vehicle_state.climate_settings.is_active is False
