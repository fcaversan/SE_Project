"""Integration tests for Flask application."""

import pytest
import json
from app import app as flask_app


@pytest.fixture
def app():
    """Create Flask app for testing."""
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_home_page(client):
    """Test home page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Vehicle Connect' in response.data


def test_settings_page(client):
    """Test settings page loads."""
    response = client.get('/settings')
    assert response.status_code == 200
    assert b'Settings' in response.data


def test_get_vehicle_status(client):
    """Test getting vehicle status API."""
    response = client.get('/api/vehicle/status')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'success' in data
    assert 'data' in data
    
    if data['success']:
        assert 'battery_soc' in data['data']
        assert 'estimated_range_km' in data['data']
        assert 'lock_status' in data['data']


def test_refresh_vehicle_status(client):
    """Test refreshing vehicle status API."""
    response = client.post('/api/vehicle/refresh')
    assert response.status_code in [200, 503]
    
    data = json.loads(response.data)
    assert 'success' in data


def test_get_user_profile(client):
    """Test getting user profile API."""
    response = client.get('/api/user/profile')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'data' in data
    assert 'unit_system' in data['data']
    assert 'temp_unit' in data['data']


def test_update_user_profile(client):
    """Test updating user profile API."""
    profile_data = {
        'user_id': 'test',
        'unit_system': 'imperial',
        'temp_unit': 'fahrenheit'
    }
    
    response = client.put(
        '/api/user/profile',
        data=json.dumps(profile_data),
        content_type='application/json'
    )
    
    assert response.status_code in [200, 400, 500]
    data = json.loads(response.data)
    assert 'success' in data


def test_404_error(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent-page')
    assert response.status_code == 404


def test_api_error_handling(client):
    """Test API error handling with invalid data."""
    response = client.put(
        '/api/user/profile',
        data='invalid json',
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['success'] is False
