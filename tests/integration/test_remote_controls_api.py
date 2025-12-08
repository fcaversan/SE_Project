"""
Integration tests for Remote Controls API endpoints.

Tests lock/unlock commands and command status polling.
"""

import pytest
import json
from datetime import datetime

from app import app
from models.vehicle_state import VehicleState
from models.enums import LockStatus


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    
    # Reset remote command service between tests
    import app as app_module
    app_module.remote_command_service = None
    
    with app.test_client() as client:
        yield client
    
    # Clean up after test
    app_module.remote_command_service = None


@pytest.fixture
def mock_vehicle_state(monkeypatch):
    """Mock vehicle state for testing."""
    state = VehicleState(
        battery_soc=75.0,
        estimated_range_km=320.0,
        lock_status=LockStatus.UNLOCKED,
        cabin_temp_celsius=20.0,
        climate_on=False,
        last_updated=datetime.now(),
        speed_mph=0.0
    )
    
    # Monkey patch get_cached_vehicle_state to return our test state
    import app as app_module
    monkeypatch.setattr(app_module, 'get_cached_vehicle_state', lambda: state)
    
    return state


class TestRemoteControlsRoutes:
    """Tests for remote controls page and API routes."""
    
    def test_controls_page_loads(self, client):
        """Test /controls page renders successfully."""
        response = client.get('/controls')
        
        assert response.status_code == 200
        assert b'Remote Controls' in response.data
        assert b'Door Locks' in response.data
    
    def test_lock_command_success(self, client, mock_vehicle_state):
        """Test POST /api/vehicle/lock returns success."""
        response = client.post('/api/vehicle/lock')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'command_id' in data
        assert data['status'] in ['pending', 'success']
    
    def test_unlock_command_success(self, client, mock_vehicle_state):
        """Test POST /api/vehicle/unlock returns success."""
        # First lock the vehicle
        mock_vehicle_state.lock_status = LockStatus.LOCKED
        
        response = client.post('/api/vehicle/unlock')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'command_id' in data
        assert data['status'] in ['pending', 'success']
    
    def test_lock_already_locked(self, client, mock_vehicle_state):
        """Test lock command fails when already locked."""
        mock_vehicle_state.lock_status = LockStatus.LOCKED
        
        response = client.post('/api/vehicle/lock')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'already locked' in data['error'].lower()
    
    def test_unlock_already_unlocked(self, client, mock_vehicle_state):
        """Test unlock command fails when already unlocked."""
        mock_vehicle_state.lock_status = LockStatus.UNLOCKED
        
        response = client.post('/api/vehicle/unlock')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'already unlocked' in data['error'].lower()
    
    def test_get_command_status_success(self, client, mock_vehicle_state):
        """Test GET /api/vehicle/commands/:id returns command status."""
        # First send a command to get a command ID
        lock_response = client.post('/api/vehicle/lock')
        lock_data = json.loads(lock_response.data)
        command_id = lock_data['command_id']
        
        # Query command status
        response = client.get(f'/api/vehicle/commands/{command_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['command_id'] == command_id
    
    def test_get_command_status_not_found(self, client):
        """Test command status returns 404 for unknown command ID."""
        fake_uuid = '550e8400-e29b-41d4-a716-446655440000'
        
        response = client.get(f'/api/vehicle/commands/{fake_uuid}')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    def test_get_command_status_invalid_id(self, client):
        """Test command status returns 400 for invalid UUID."""
        response = client.get('/api/vehicle/commands/invalid-uuid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'invalid' in data['error'].lower()
    
    def test_lock_unlock_sequence(self, client, mock_vehicle_state):
        """Test complete lock → unlock → lock sequence."""
        # Start unlocked
        mock_vehicle_state.lock_status = LockStatus.UNLOCKED
        
        # Lock
        lock_response = client.post('/api/vehicle/lock')
        assert lock_response.status_code == 200
        
        # Unlock
        unlock_response = client.post('/api/vehicle/unlock')
        assert unlock_response.status_code == 200
        
        # Lock again
        lock_response2 = client.post('/api/vehicle/lock')
        assert lock_response2.status_code == 200
