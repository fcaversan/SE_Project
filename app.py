"""
Vehicle Connect - Main Flask application.

Flask web server for Home Screen & Vehicle Status feature.
"""

import os
from flask import Flask, render_template, jsonify, request
from models import VehicleState, UserProfile
from models.remote_command import RemoteCommand
from models.climate_settings import ClimateSettings
from models.enums import CommandType, SeatHeatLevel
from services import safe_read_json, atomic_write_json, ensure_directory
from mocks import VehicleDataMockService
from mocks.remote_command_mock import RemoteCommandMockService

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Paths for data persistence
DATA_DIR = 'data'
VEHICLE_STATE_FILE = os.path.join(DATA_DIR, 'vehicle_state.json')
USER_PROFILE_FILE = os.path.join(DATA_DIR, 'user_settings.json')

# Initialize mock services (configurable via environment)
mock_delay = float(os.environ.get('MOCK_DELAY', '0.5'))
mock_scenario = os.environ.get('MOCK_SCENARIO', 'normal')
vehicle_service = VehicleDataMockService(delay_seconds=mock_delay, scenario=mock_scenario)

# Initialize remote command service (shares vehicle state with vehicle_service)
remote_command_service = None  # Lazy initialization to share vehicle state


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


def get_remote_command_service() -> RemoteCommandMockService:
    """Get or create remote command service instance."""
    global remote_command_service
    if remote_command_service is None:
        # Get current vehicle state to share with remote command service
        state = get_cached_vehicle_state()
        remote_command_service = RemoteCommandMockService(
            vehicle_state=state,
            success_rate=0.95,
            min_delay_ms=1000,
            max_delay_ms=2500
        )
    return remote_command_service


def cache_vehicle_state(state: VehicleState) -> bool:
    """Save vehicle state to cache file."""
    ensure_directory(VEHICLE_STATE_FILE)
    return atomic_write_json(VEHICLE_STATE_FILE, state.to_dict())


@app.route('/')
def home():
    """Render home screen."""
    return render_template('home.html')


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

@app.route('/api/vehicle/lock', methods=['POST'])
def lock_vehicle():
    """Lock vehicle doors."""
    try:
        service = get_remote_command_service()
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
        service = get_remote_command_service()
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
        service = get_remote_command_service()
        
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
        service = get_remote_command_service()
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
        service = get_remote_command_service()
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
        service = get_remote_command_service()
        data = request.get_json() or {}
        
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
        service = get_remote_command_service()
        data = request.get_json() or {}
        
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
        service = get_remote_command_service()
        data = request.get_json() or {}
        
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
        service = get_remote_command_service()
        
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
        service = get_remote_command_service()
        
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
        service = get_remote_command_service()
        
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
