"""
Vehicle Connect - Main Flask application.

Flask web server for Home Screen & Vehicle Status feature.
"""

import os
from flask import Flask, render_template, jsonify, request
from models import VehicleState, UserProfile
from models.remote_command import RemoteCommand
from models.climate_settings import ClimateSettings
from models.charging_schedule import ChargingSchedule
from models.destination import Destination
from models.route import Route
from models.trip_history import TripHistory
from models.enums import CommandType, SeatHeatLevel
from services import safe_read_json, atomic_write_json, ensure_directory
from services.navigation_service import NavigationService
from mocks import VehicleDataMockService
from mocks.remote_command_mock import RemoteCommandMockService
from mocks.charging_mock import ChargingMockService

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Paths for data persistence
DATA_DIR = 'data'
VEHICLE_STATE_FILE = os.path.join(DATA_DIR, 'vehicle_state.json')
USER_PROFILE_FILE = os.path.join(DATA_DIR, 'user_settings.json')


def cache_vehicle_state(state: VehicleState) -> bool:
    """Save vehicle state to cache file."""
    ensure_directory(VEHICLE_STATE_FILE)
    return atomic_write_json(VEHICLE_STATE_FILE, state.to_dict())


def get_or_create_initial_state() -> VehicleState:
    """Get cached state or create new one."""
    ensure_directory(VEHICLE_STATE_FILE)
    data = safe_read_json(VEHICLE_STATE_FILE)
    if data:
        return VehicleState.from_dict(data)
    # Create new state and cache it
    from mocks.vehicle_data_mock import VehicleDataMockService
    temp_service = VehicleDataMockService(delay_seconds=0, scenario=os.environ.get('MOCK_SCENARIO', 'normal'))
    initial_state = temp_service.get_vehicle_state()
    cache_vehicle_state(initial_state)
    return initial_state


# Initialize mock services (configurable via environment)
mock_delay = float(os.environ.get('MOCK_DELAY', '0.5'))
mock_scenario = os.environ.get('MOCK_SCENARIO', 'normal')

# Create shared vehicle state
shared_vehicle_state = get_or_create_initial_state()

# Initialize services with shared state
vehicle_service = VehicleDataMockService(
    delay_seconds=mock_delay, 
    scenario=mock_scenario,
    initial_state=shared_vehicle_state
)

remote_command_mock = RemoteCommandMockService(shared_vehicle_state)
charging_mock = ChargingMockService(shared_vehicle_state)

# Initialize remote command service with same shared state
remote_command_service = RemoteCommandMockService(
    vehicle_state=shared_vehicle_state,
    success_rate=1.0,  # 100% success by default, toggle via UI
    min_delay_ms=1000,
    max_delay_ms=2500
)

# Initialize charging service with shared state
charging_service = ChargingMockService(
    vehicle_state=shared_vehicle_state,
    data_dir=DATA_DIR,
    battery_capacity_kwh=82.0,
    max_charging_rate_kw=250.0
)

# Initialize navigation service (use charging service's stations)
navigation_service = NavigationService(charging_stations=charging_service.get_nearby_stations())


def get_user_profile() -> UserProfile:
    """Load user profile from data file or return default."""
    ensure_directory(USER_PROFILE_FILE)
    data = safe_read_json(USER_PROFILE_FILE)
    if data:
        return UserProfile.from_dict(data)
    return UserProfile.get_default()


def save_user_profile(profile: UserProfile) -> bool:
    """Save user profile to data file."""
    ensure_directory(USER_PROFILE_FILE)
    return atomic_write_json(USER_PROFILE_FILE, profile.to_dict())


def get_cached_vehicle_state() -> VehicleState:
    """Load cached vehicle state from data file."""
    ensure_directory(VEHICLE_STATE_FILE)
    data = safe_read_json(VEHICLE_STATE_FILE)
    if data:
        return VehicleState.from_dict(data)
    # Return fresh state if no cache
    return vehicle_service.get_vehicle_state()


@app.route('/')
def home():
    """Render home screen."""
    return render_template('home.html')


@app.route('/charging')
def charging():
    """Render charging management page."""
    return render_template('charging.html')


@app.route('/stations')
def stations():
    """Render charging stations page."""
    return render_template('stations.html')


@app.route('/api/vehicle/status', methods=['GET'])
def get_vehicle_status():
    """
    Get current vehicle status.
    
    Returns cached data with fresh flag, or attempts to fetch fresh data.
    """
    try:
        # Try to get fresh data from service
        state = vehicle_service.get_vehicle_state()
        cache_vehicle_state(state)
        
        return jsonify({
            'success': True,
            'data': state.to_dict(),
            'is_stale': state.is_stale(),
            'warnings': {
                'low_battery': state.is_low_battery(),
                'critical_battery': state.is_critical_battery(),
                'unlocked_too_long': state.is_unlocked_too_long()
            }
        })
    except Exception as e:
        # On error, return cached data if available
        try:
            cached_state = get_cached_vehicle_state()
            return jsonify({
                'success': False,
                'error': str(e),
                'data': cached_state.to_dict(),
                'is_stale': True,
                'warnings': {
                    'low_battery': cached_state.is_low_battery(),
                    'critical_battery': cached_state.is_critical_battery(),
                    'unlocked_too_long': cached_state.is_unlocked_too_long()
                }
            }), 503
        except Exception:
            return jsonify({
                'success': False,
                'error': 'Unable to reach vehicle and no cached data available'
            }), 503


@app.route('/api/vehicle/refresh', methods=['POST'])
def refresh_vehicle_status():
    """Force refresh of vehicle data."""
    try:
        state = vehicle_service.refresh_data()
        cache_vehicle_state(state)
        
        return jsonify({
            'success': True,
            'data': state.to_dict(),
            'is_stale': False,
            'warnings': {
                'low_battery': state.is_low_battery(),
                'critical_battery': state.is_critical_battery(),
                'unlocked_too_long': state.is_unlocked_too_long()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 503


@app.route('/api/user/profile', methods=['GET'])
def get_user_preferences():
    """Get user profile and preferences."""
    profile = get_user_profile()
    return jsonify({
        'success': True,
        'data': profile.to_dict()
    })


@app.route('/api/user/profile', methods=['PUT'])
def update_user_preferences():
    """Update user profile and preferences."""
    try:
        data = request.get_json()
        profile = UserProfile.from_dict(data)
        success = save_user_profile(profile)
        
        if success:
            return jsonify({
                'success': True,
                'data': profile.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save preferences'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/settings')
def settings():
    """Render settings page."""
    return render_template('settings.html')


@app.route('/controls')
def controls():
    """Render remote controls page."""
    return render_template('controls.html')


# Remote Controls API Endpoints

@app.route('/api/mock/toggle', methods=['POST'])
def toggle_mock_mode():
    """Toggle mock service between success and failure modes."""
    try:
        data = request.get_json() or {}
        fail_mode = data.get('fail_mode', False)
        
        # Set success rate: 0.0 for fail mode, 1.0 for success mode
        remote_command_service.success_rate = 0.0 if fail_mode else 1.0
        
        return jsonify({
            'success': True,
            'fail_mode': fail_mode,
            'success_rate': remote_command_service.success_rate
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/mock/status', methods=['GET'])
def get_mock_status():
    """Get current mock service configuration."""
    try:
        fail_mode = remote_command_service.success_rate == 0.0
        
        return jsonify({
            'success': True,
            'fail_mode': fail_mode,
            'success_rate': remote_command_service.success_rate
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vehicle/lock', methods=['POST'])
def lock_vehicle():
    """Lock vehicle doors."""
    try:
        service = remote_command_service
        command = RemoteCommand(command_type=CommandType.LOCK)
        
        result = service.send_command(command)
        
        # Cache updated vehicle state
        cache_vehicle_state(service.vehicle_state)
        
        return jsonify({
            'success': True,
            'command_id': str(result.command_id),
            'status': result.status.value
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vehicle/unlock', methods=['POST'])
def unlock_vehicle():
    """Unlock vehicle doors."""
    try:
        service = remote_command_service
        command = RemoteCommand(command_type=CommandType.UNLOCK)
        
        result = service.send_command(command)
        
        # Cache updated vehicle state
        cache_vehicle_state(service.vehicle_state)
        
        return jsonify({
            'success': True,
            'command_id': str(result.command_id),
            'status': result.status.value
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/vehicle/commands/<command_id>', methods=['GET'])
def get_command_status(command_id):
    """Get status of a remote command."""
    try:
        from uuid import UUID
        service = remote_command_service
        
        command = service.get_command_status(UUID(command_id))
        
        if command is None:
            return jsonify({
                'success': False,
                'error': 'Command not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': command.to_dict()
        })
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid command ID'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vehicle/climate', methods=['POST'])
def control_climate():
    """Start or stop climate control."""
    try:
        service = remote_command_service
        data = request.get_json() or {}
        
        # Get the action (start/stop)
        action = data.get('action', 'start')
        
        # Safety check: reject if battery too low
        if action == 'start' and service.vehicle_state.battery_soc < 10:
            return jsonify({
                'success': False,
                'error': 'Battery too low for climate control'
            }), 400
        
        if action == 'start':
            # Get climate settings from request
            temp = data.get('temperature', 21.0)
            
            # Validate temperature range
            if not 15.0 <= temp <= 28.0:
                return jsonify({
                    'success': False,
                    'error': 'Temperature must be between 15°C and 28°C'
                }), 400
            
            # Build climate settings
            climate_settings = ClimateSettings(
                is_active=True,
                target_temp_celsius=temp,
                is_plugged_in=service.vehicle_state.is_plugged_in
            )
            
            # Create and send command
            command = RemoteCommand(
                command_type=CommandType.CLIMATE_ON,
                parameters={'target_temp': temp}
            )
            
            result = service.send_command(command)
            
            # Calculate battery drain estimate
            current_temp = service.vehicle_state.cabin_temp_celsius
            drain_estimate = climate_settings.estimate_battery_drain_per_10min(current_temp)
            
            # Cache updated vehicle state
            cache_vehicle_state(service.vehicle_state)
            
            return jsonify({
                'success': True,
                'command_id': str(result.command_id),
                'status': result.status.value,
                'battery_drain_estimate': drain_estimate,
                'is_plugged_in': service.vehicle_state.is_plugged_in
            })
        else:
            # Stop climate
            command = RemoteCommand(command_type=CommandType.CLIMATE_OFF)
            result = service.send_command(command)
            
            # Cache updated vehicle state
            cache_vehicle_state(service.vehicle_state)
            
            return jsonify({
                'success': True,
                'command_id': str(result.command_id),
                'status': result.status.value
            })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vehicle/climate', methods=['PUT'])
def update_climate():
    """Update climate control settings while running."""
    try:
        service = remote_command_service
        data = request.get_json() or {}
        
        # Check if climate is currently active
        if not service.vehicle_state.climate_settings or not service.vehicle_state.climate_settings.is_active:
            return jsonify({
                'success': False,
                'error': 'Climate control is not active'
            }), 400
        
        # Get current settings
        current = service.vehicle_state.climate_settings
        
        # Update temperature if provided
        temp = data.get('temperature', current.target_temp_celsius)
        
        # Validate temperature range
        if not 15.0 <= temp <= 28.0:
            return jsonify({
                'success': False,
                'error': 'Temperature must be between 15°C and 28°C'
            }), 400
        
        # Build updated climate settings
        climate_settings = ClimateSettings(
            is_active=True,
            target_temp_celsius=temp,
            front_left_seat_heat=current.front_left_seat_heat,
            front_right_seat_heat=current.front_right_seat_heat,
            rear_seat_heat=current.rear_seat_heat,
            steering_wheel_heat=current.steering_wheel_heat,
            front_defrost=current.front_defrost,
            rear_defrost=current.rear_defrost,
            is_plugged_in=service.vehicle_state.is_plugged_in
        )
        
        # Create and send command
        command = RemoteCommand(
            command_type=CommandType.SET_TEMP,
            parameters={'target_temp': temp}
        )
        
        result = service.send_command(command)
        
        # Calculate battery drain estimate
        current_temp = service.vehicle_state.cabin_temp_celsius
        drain_estimate = climate_settings.estimate_battery_drain_per_10min(current_temp)
        
        # Cache updated vehicle state
        cache_vehicle_state(service.vehicle_state)
        
        return jsonify({
            'success': True,
            'command_id': str(result.command_id),
            'status': result.status.value,
            'battery_drain_estimate': drain_estimate
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vehicle/seat-heat', methods=['POST'])
def control_seat_heat():
    """Control heated seats."""
    try:
        service = remote_command_service
        data = request.get_json() or {}
        
        # Check if climate is on
        if not service.vehicle_state.climate_on:
            return jsonify({
                'success': False,
                'error': 'Climate control must be active to use heated seats'
            }), 400
        
        # Get seat position and level
        seat = data.get('seat', 'front_left')  # front_left, front_right, rear
        level = data.get('level', 'off')  # off, low, medium, high
        
        # Validate seat position
        if seat not in ['front_left', 'front_right', 'rear']:
            return jsonify({
                'success': False,
                'error': 'Invalid seat position'
            }), 400
        
        # Validate heat level
        try:
            heat_level = SeatHeatLevel(level)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid heat level. Use: off, low, medium, high'
            }), 400
        
        # Create and send command
        command = RemoteCommand(
            command_type=CommandType.SEAT_HEAT,
            parameters={'seat': seat, 'level': level}
        )
        
        result = service.send_command(command)
        
        # Cache updated vehicle state
        cache_vehicle_state(service.vehicle_state)
        
        return jsonify({
            'success': True,
            'command_id': str(result.command_id),
            'status': result.status.value
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vehicle/steering-heat', methods=['POST'])
def control_steering_heat():
    """Control heated steering wheel."""
    try:
        service = remote_command_service
        data = request.get_json() or {}
        
        # Check if climate is on
        if not service.vehicle_state.climate_on:
            return jsonify({
                'success': False,
                'error': 'Climate control must be active to use heated steering wheel'
            }), 400
        
        # Get enabled state
        enabled = data.get('enabled', False)
        
        # Create and send command
        command = RemoteCommand(
            command_type=CommandType.STEERING_HEAT,
            parameters={'enabled': enabled}
        )
        
        result = service.send_command(command)
        
        # Cache updated vehicle state
        cache_vehicle_state(service.vehicle_state)
        
        return jsonify({
            'success': True,
            'command_id': str(result.command_id),
            'status': result.status.value
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vehicle/defrost', methods=['POST'])
def control_defrost():
    """Control defrost (front/rear)."""
    try:
        service = remote_command_service
        data = request.get_json() or {}
        
        # Check if climate is on
        if not service.vehicle_state.climate_on:
            return jsonify({
                'success': False,
                'error': 'Climate control must be active to use defrost'
            }), 400
        
        # Get position and enabled state
        position = data.get('position', 'front')  # front or rear
        enabled = data.get('enabled', False)
        
        # Validate position
        if position not in ['front', 'rear']:
            return jsonify({
                'success': False,
                'error': 'Invalid position. Use: front or rear'
            }), 400
        
        # Create and send command
        command = RemoteCommand(
            command_type=CommandType.DEFROST,
            parameters={'position': position, 'enabled': enabled}
        )
        
        result = service.send_command(command)
        
        # Cache updated vehicle state
        cache_vehicle_state(service.vehicle_state)
        
        return jsonify({
            'success': True,
            'command_id': str(result.command_id),
            'status': result.status.value
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vehicle/trunk/open', methods=['POST'])
def open_trunk():
    """Open rear trunk."""
    try:
        service = remote_command_service
        
        # Safety check: reject if vehicle is moving
        if service.vehicle_state.speed_mph > 0:
            return jsonify({
                'success': False,
                'error': 'Cannot open trunk while vehicle is moving'
            }), 400
        
        # Create and send command
        command = RemoteCommand(
            command_type=CommandType.TRUNK_OPEN,
            parameters={}
        )
        
        result = service.send_command(command)
        
        # Cache updated vehicle state
        cache_vehicle_state(service.vehicle_state)
        
        return jsonify({
            'success': True,
            'command_id': str(result.command_id),
            'status': result.status.value
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vehicle/frunk/open', methods=['POST'])
def open_frunk():
    """Open front trunk (frunk)."""
    try:
        service = remote_command_service
        
        # Safety check: reject if vehicle is moving
        if service.vehicle_state.speed_mph > 0:
            return jsonify({
                'success': False,
                'error': 'Cannot open frunk while vehicle is moving'
            }), 400
        
        # Create and send command
        command = RemoteCommand(
            command_type=CommandType.FRUNK_OPEN,
            parameters={}
        )
        
        result = service.send_command(command)
        
        # Cache updated vehicle state
        cache_vehicle_state(service.vehicle_state)
        
        return jsonify({
            'success': True,
            'command_id': str(result.command_id),
            'status': result.status.value
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/vehicle/honk-flash', methods=['POST'])
def honk_flash():
    """Honk horn and flash lights to locate vehicle."""
    try:
        service = remote_command_service
        
        # Create and send command
        command = RemoteCommand(
            command_type=CommandType.HONK_FLASH,
            parameters={}
        )
        
        result = service.send_command(command)
        
        # Cache updated vehicle state
        cache_vehicle_state(service.vehicle_state)
        
        return jsonify({
            'success': True,
            'command_id': str(result.command_id),
            'status': result.status.value
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# CHARGING MANAGEMENT ENDPOINTS (Phase 3: FR-CHG-001 through FR-CHG-008)
# ============================================================================

@app.route('/api/charging/start', methods=['POST'])
def start_charging():
    """Start a charging session (FR-CHG-001)."""
    try:
        data = request.get_json()
        target_soc = data.get('target_soc', 80)  # Default to 80%
        
        session = charging_service.start_charging(target_soc)
        
        # Cache updated vehicle state
        cache_vehicle_state(charging_service.vehicle_state)
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charging/stop', methods=['POST'])
def stop_charging():
    """Stop the active charging session (FR-CHG-001)."""
    try:
        session = charging_service.stop_charging()
        
        # Cache updated vehicle state
        cache_vehicle_state(charging_service.vehicle_state)
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charging/status', methods=['GET'])
def get_charging_status():
    """Get current charging status (FR-CHG-002)."""
    try:
        current_session = charging_service.get_current_session()
        
        return jsonify({
            'success': True,
            'is_charging': current_session is not None and current_session.is_active,
            'session': current_session.to_dict() if current_session else None,
            'charge_limit': charging_service.get_charge_limit()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charging/history', methods=['GET'])
def get_charging_history():
    """Get charging session history (FR-CHG-002)."""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = charging_service.get_charging_history(limit)
        
        return jsonify({
            'success': True,
            'sessions': [s.to_dict() for s in history]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charging/limit', methods=['GET'])
def get_charge_limit():
    """Get the current charge limit (FR-CHG-003)."""
    try:
        limit = charging_service.get_charge_limit()
        
        return jsonify({
            'success': True,
            'charge_limit': limit
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charging/limit', methods=['PUT'])
def set_charge_limit():
    """Set the charge limit (FR-CHG-003)."""
    try:
        data = request.get_json()
        limit = data.get('limit')
        
        if limit is None:
            return jsonify({
                'success': False,
                'error': 'Missing required field: limit'
            }), 400
        
        new_limit = charging_service.set_charge_limit(limit)
        
        return jsonify({
            'success': True,
            'charge_limit': new_limit
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charging/schedules', methods=['GET'])
def get_schedules():
    """Get all charging schedules (FR-CHG-004)."""
    try:
        schedules = charging_service.get_schedules()
        
        return jsonify({
            'success': True,
            'schedules': [s.to_dict() for s in schedules]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charging/schedules', methods=['POST'])
def create_schedule():
    """Create a new charging schedule (FR-CHG-004)."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['name', 'days_of_week', 'target_soc']
        for field in required:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Must have either start_time or ready_by_time
        if 'start_time' not in data and 'ready_by_time' not in data:
            return jsonify({
                'success': False,
                'error': 'Must provide either start_time or ready_by_time'
            }), 400
        
        schedule = ChargingSchedule(
            name=data['name'],
            days_of_week=data['days_of_week'],
            start_time=data.get('start_time'),
            ready_by_time=data.get('ready_by_time'),
            target_soc=data['target_soc'],
            enabled=data.get('enabled', True)
        )
        
        created = charging_service.create_schedule(schedule)
        
        return jsonify({
            'success': True,
            'schedule': created.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charging/schedules/<schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    """Update an existing charging schedule (FR-CHG-004)."""
    try:
        data = request.get_json()
        
        # Get existing schedules to find the one to update
        schedules = charging_service.get_schedules()
        existing = next((s for s in schedules if s.schedule_id == schedule_id), None)
        
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404
        
        # Update fields
        if 'name' in data:
            existing.name = data['name']
        if 'days_of_week' in data:
            existing.days_of_week = data['days_of_week']
        if 'start_time' in data:
            existing.start_time = data['start_time']
            existing.ready_by_time = None  # Clear the other time field
        if 'ready_by_time' in data:
            existing.ready_by_time = data['ready_by_time']
            existing.start_time = None  # Clear the other time field
        if 'target_soc' in data:
            existing.target_soc = data['target_soc']
        if 'enabled' in data:
            existing.enabled = data['enabled']
        
        updated = charging_service.update_schedule(existing)
        
        return jsonify({
            'success': True,
            'schedule': updated.to_dict()
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charging/schedules/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    """Delete a charging schedule (FR-CHG-004)."""
    try:
        success = charging_service.delete_schedule(schedule_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404
        
        return jsonify({
            'success': True
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/charging/stations', methods=['GET'])
def get_charging_stations():
    """Get nearby charging stations (FR-CHG-005, FR-CHG-006, FR-CHG-007)."""
    try:
        # Parse query parameters
        max_distance = request.args.get('max_distance_km', 10.0, type=float)
        connector_filter = request.args.getlist('connector_types')  # Can pass multiple
        power_filter = request.args.get('min_power_kw', type=int)
        
        stations = charging_service.get_nearby_stations(
            max_distance_km=max_distance,
            connector_filter=connector_filter if connector_filter else None,
            power_filter=power_filter
        )
        
        return jsonify({
            'success': True,
            'stations': [s.to_dict() for s in stations],
            'count': len(stations)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =============================================================================
# NAVIGATION & TRIP PLANNING ROUTES (FR-TRP)
# =============================================================================

@app.route('/navigation')
def navigation():
    """Render navigation and trip planning page (FR-TRP-001)."""
    return render_template('navigation.html')


@app.route('/api/navigation/search', methods=['GET'])
def search_destinations():
    """Search for destinations (FR-TRP-001)."""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        destinations = navigation_service.search_destinations(query)
        
        return jsonify({
            'success': True,
            'destinations': [d.to_dict() for d in destinations]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/navigation/calculate-route', methods=['POST'])
def calculate_route():
    """Calculate route with charging stops (FR-TRP-002, FR-TRP-003)."""
    try:
        data = request.get_json()
        
        if not data or 'destination' not in data:
            return jsonify({
                'success': False,
                'error': 'Destination required'
            }), 400
        
        # Get destination
        dest_data = data['destination']
        destination = Destination.from_dict(dest_data)
        
        # Get current SoC
        current_soc = data.get('current_soc', 80.0)
        elevation_gain_m = data.get('elevation_gain_m', 0)
        
        # Create origin (vehicle's current location)
        # In production, would get actual vehicle location
        origin = Destination(
            name="Current Location",
            address="San Francisco, CA",
            latitude=37.7749,
            longitude=-122.4194
        )
        
        # Calculate route
        route = navigation_service.calculate_route(
            origin=origin,
            destination=destination,
            current_soc=current_soc,
            elevation_gain_m=elevation_gain_m
        )
        
        return jsonify({
            'success': True,
            'route': route.to_dict()
        })
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/navigation/send-to-vehicle', methods=['POST'])
def send_route_to_vehicle():
    """Send route to vehicle's navigation system (FR-TRP-001)."""
    try:
        data = request.get_json()
        
        if not data or 'route' not in data:
            return jsonify({
                'success': False,
                'error': 'Route required'
            }), 400
        
        # In production, would send to actual vehicle
        # For now, just acknowledge success
        
        return jsonify({
            'success': True,
            'message': 'Route sent to vehicle navigation system'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/navigation/recent-trips', methods=['GET'])
def get_recent_trips():
    """Get recent trip history (FR-TRP-004)."""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        trips = navigation_service.get_recent_trips(limit=limit)
        
        return jsonify({
            'success': True,
            'trips': [t.to_dict() for t in trips]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', error_code=404, error_message='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('error.html', error_code=500, error_message='Internal server error'), 500


if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Run development server
    app.run(debug=True, host='127.0.0.1', port=5000)
