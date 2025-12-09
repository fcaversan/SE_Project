"""
Integration tests for Charging Management API endpoints.

Tests all charging-related endpoints (FR-CHG-001 through FR-CHG-008).
"""

import pytest
import json
from app import app


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def reset_charging_state(client):
    """Reset charging state before each test."""
    # Import here to access the app's shared state
    from app import shared_vehicle_state
    
    # Ensure vehicle is plugged in for charging tests
    shared_vehicle_state.is_plugged_in = True
    # Set battery to 50% so we can test charging
    shared_vehicle_state.battery_soc = 50.0
    
    # Stop any active charging
    try:
        client.post('/api/charging/stop')
    except:
        pass
    yield


class TestChargingStartStop:
    """Tests for start/stop charging endpoints (FR-CHG-001)."""
    
    def test_start_charging_success(self, client, reset_charging_state):
        """Test starting a charging session."""
        # Start charging
        response = client.post('/api/charging/start',
                             json={'target_soc': 80})
        
        if response.status_code != 200:
            # Debug: print error
            data = json.loads(response.data)
            print(f"Error: {data}")
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'session' in data
        assert data['session']['is_active'] is True
        assert data['session']['target_soc'] == 80
    
    def test_start_charging_custom_target(self, client, reset_charging_state):
        """Test starting charging with custom target SoC."""
        response = client.post('/api/charging/start',
                             json={'target_soc': 90})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['session']['target_soc'] == 90
    
    def test_start_charging_invalid_target(self, client, reset_charging_state):
        """Test starting charging with invalid target."""
        response = client.post('/api/charging/start',
                             json={'target_soc': 101})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_stop_charging_success(self, client, reset_charging_state):
        """Test stopping an active charging session."""
        # Start charging first
        client.post('/api/charging/start', json={'target_soc': 80})
        
        # Stop charging
        response = client.post('/api/charging/stop')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'session' in data
        assert data['session']['is_active'] is False
        assert data['session']['end_time'] is not None
    
    def test_stop_charging_no_active_session(self, client, reset_charging_state):
        """Test stopping when no session is active."""
        response = client.post('/api/charging/stop')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data


class TestChargingStatus:
    """Tests for charging status endpoints (FR-CHG-002)."""
    
    def test_get_status_not_charging(self, client, reset_charging_state):
        """Test getting status when not charging."""
        response = client.get('/api/charging/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['is_charging'] is False
        assert data['session'] is None
        assert 'charge_limit' in data
    
    def test_get_status_while_charging(self, client, reset_charging_state):
        """Test getting status during active charging."""
        # Start charging
        client.post('/api/charging/start', json={'target_soc': 80})
        
        response = client.get('/api/charging/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['is_charging'] is True
        assert data['session'] is not None
        assert data['session']['is_active'] is True
    
    def test_get_history_empty(self, client):
        """Test getting history when empty."""
        response = client.get('/api/charging/history')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert isinstance(data['sessions'], list)
    
    def test_get_history_with_limit(self, client):
        """Test getting history with limit parameter."""
        response = client.get('/api/charging/history?limit=5')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['sessions']) <= 5


class TestChargeLimit:
    """Tests for charge limit endpoints (FR-CHG-003)."""
    
    def test_get_charge_limit(self, client):
        """Test getting current charge limit."""
        response = client.get('/api/charging/limit')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'charge_limit' in data
        assert 1 <= data['charge_limit'] <= 100
    
    def test_set_charge_limit_success(self, client):
        """Test setting charge limit."""
        response = client.put('/api/charging/limit',
                            json={'limit': 85})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['charge_limit'] == 85
        
        # Verify it persisted
        response = client.get('/api/charging/limit')
        data = json.loads(response.data)
        assert data['charge_limit'] == 85
    
    def test_set_charge_limit_invalid(self, client):
        """Test setting invalid charge limit."""
        response = client.put('/api/charging/limit',
                            json={'limit': 0})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        
        response = client.put('/api/charging/limit',
                            json={'limit': 101})
        
        assert response.status_code == 400
    
    def test_set_charge_limit_missing_field(self, client):
        """Test setting charge limit without limit field."""
        response = client.put('/api/charging/limit', json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data


class TestChargingSchedules:
    """Tests for charging schedule endpoints (FR-CHG-004)."""
    
    def test_get_schedules_empty(self, client):
        """Test getting schedules when none exist."""
        response = client.get('/api/charging/schedules')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert isinstance(data['schedules'], list)
    
    def test_create_schedule_with_start_time(self, client):
        """Test creating schedule with start_time."""
        schedule_data = {
            'name': 'Weeknight Charging',
            'days_of_week': [0, 1, 2, 3, 4],
            'start_time': '22:00',
            'target_soc': 80,
            'enabled': True
        }
        
        response = client.post('/api/charging/schedules',
                             json=schedule_data)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['schedule']['name'] == 'Weeknight Charging'
        assert data['schedule']['start_time'] == '22:00'
        assert data['schedule']['target_soc'] == 80
    
    def test_create_schedule_with_ready_by(self, client):
        """Test creating schedule with ready_by_time."""
        schedule_data = {
            'name': 'Morning Ready',
            'days_of_week': [0, 1, 2, 3, 4],
            'ready_by_time': '07:00',
            'target_soc': 90
        }
        
        response = client.post('/api/charging/schedules',
                             json=schedule_data)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['schedule']['ready_by_time'] == '07:00'
    
    def test_create_schedule_missing_fields(self, client):
        """Test creating schedule with missing required fields."""
        response = client.post('/api/charging/schedules',
                             json={'name': 'Test'})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_create_schedule_no_time_fields(self, client):
        """Test creating schedule without start_time or ready_by_time."""
        schedule_data = {
            'name': 'Invalid Schedule',
            'days_of_week': [0, 1],
            'target_soc': 80
        }
        
        response = client.post('/api/charging/schedules',
                             json=schedule_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_schedule_success(self, client):
        """Test updating an existing schedule."""
        # Create schedule first
        create_data = {
            'name': 'Test Schedule',
            'days_of_week': [0, 1],
            'start_time': '22:00',
            'target_soc': 80
        }
        response = client.post('/api/charging/schedules',
                             json=create_data)
        schedule_id = json.loads(response.data)['schedule']['schedule_id']
        
        # Update it
        update_data = {
            'name': 'Updated Schedule',
            'target_soc': 90,
            'enabled': False
        }
        response = client.put(f'/api/charging/schedules/{schedule_id}',
                            json=update_data)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['schedule']['name'] == 'Updated Schedule'
        assert data['schedule']['target_soc'] == 90
        assert data['schedule']['enabled'] is False
    
    def test_update_schedule_not_found(self, client):
        """Test updating non-existent schedule."""
        response = client.put('/api/charging/schedules/nonexistent-id',
                            json={'name': 'Test'})
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_delete_schedule_success(self, client):
        """Test deleting a schedule."""
        # Create schedule first
        create_data = {
            'name': 'To Delete',
            'days_of_week': [0],
            'start_time': '22:00',
            'target_soc': 80
        }
        response = client.post('/api/charging/schedules',
                             json=create_data)
        schedule_id = json.loads(response.data)['schedule']['schedule_id']
        
        # Delete it
        response = client.delete(f'/api/charging/schedules/{schedule_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify it's gone
        response = client.get('/api/charging/schedules')
        data = json.loads(response.data)
        schedule_ids = [s['schedule_id'] for s in data['schedules']]
        assert schedule_id not in schedule_ids
    
    def test_delete_schedule_not_found(self, client):
        """Test deleting non-existent schedule."""
        response = client.delete('/api/charging/schedules/nonexistent-id')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False


class TestChargingStations:
    """Tests for charging station endpoints (FR-CHG-005, FR-CHG-006, FR-CHG-007)."""
    
    def test_get_stations_default(self, client):
        """Test getting stations with default parameters."""
        response = client.get('/api/charging/stations')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'stations' in data
        assert 'count' in data
        assert isinstance(data['stations'], list)
    
    def test_get_stations_with_distance_filter(self, client):
        """Test filtering stations by distance."""
        response = client.get('/api/charging/stations?max_distance_km=5.0')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        for station in data['stations']:
            assert station['distance_km'] <= 5.0
    
    def test_get_stations_with_connector_filter(self, client):
        """Test filtering stations by connector type."""
        response = client.get('/api/charging/stations?connector_types=tesla&connector_types=ccs')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        for station in data['stations']:
            connectors = station['connector_types']
            assert 'tesla' in connectors or 'ccs' in connectors
    
    def test_get_stations_with_power_filter(self, client):
        """Test filtering stations by power level."""
        response = client.get('/api/charging/stations?min_power_kw=150')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        for station in data['stations']:
            max_power = max(station['power_levels_kw'])
            assert max_power >= 150
    
    def test_get_stations_combined_filters(self, client):
        """Test combining multiple filters."""
        response = client.get(
            '/api/charging/stations?'
            'max_distance_km=3.0&'
            'connector_types=tesla&'
            'min_power_kw=200'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        for station in data['stations']:
            assert station['distance_km'] <= 3.0
            assert 'tesla' in station['connector_types']
            assert max(station['power_levels_kw']) >= 200
    
    def test_get_stations_sorted_by_distance(self, client):
        """Test that stations are sorted by distance."""
        response = client.get('/api/charging/stations')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        if len(data['stations']) > 1:
            distances = [s['distance_km'] for s in data['stations']]
            assert distances == sorted(distances)
