"""
Unit tests for RemoteCommand model.

Tests command creation, status transitions, and serialization.
"""

import pytest
from datetime import datetime
from uuid import UUID

from models.remote_command import RemoteCommand
from models.enums import CommandType, CommandStatus


class TestRemoteCommand:
    """Tests for RemoteCommand model."""
    
    def test_create_command_with_defaults(self):
        """Test creating command with minimal parameters."""
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        
        assert cmd.command_type == CommandType.LOCK
        assert cmd.status == CommandStatus.PENDING
        assert cmd.parameters == {}
        assert cmd.response_time is None
        assert cmd.error_message is None
        assert isinstance(cmd.command_id, UUID)
        assert isinstance(cmd.timestamp, datetime)
    
    def test_create_command_with_parameters(self):
        """Test creating command with custom parameters."""
        params = {'target_temp': 21.5, 'seat': 'front_left'}
        cmd = RemoteCommand(
            command_type=CommandType.SET_TEMP,
            parameters=params
        )
        
        assert cmd.command_type == CommandType.SET_TEMP
        assert cmd.parameters == params
        assert cmd.status == CommandStatus.PENDING
    
    def test_mark_success(self):
        """Test marking command as successful."""
        cmd = RemoteCommand(command_type=CommandType.UNLOCK)
        
        cmd.mark_success(response_time_ms=1523)
        
        assert cmd.status == CommandStatus.SUCCESS
        assert cmd.response_time == 1523
        assert cmd.error_message is None
    
    def test_mark_failed(self):
        """Test marking command as failed."""
        cmd = RemoteCommand(command_type=CommandType.CLIMATE_ON)
        
        cmd.mark_failed("Battery too low", response_time_ms=850)
        
        assert cmd.status == CommandStatus.FAILED
        assert cmd.error_message == "Battery too low"
        assert cmd.response_time == 850
    
    def test_mark_failed_without_response_time(self):
        """Test marking command as failed without response time."""
        cmd = RemoteCommand(command_type=CommandType.TRUNK_OPEN)
        
        cmd.mark_failed("Vehicle is moving")
        
        assert cmd.status == CommandStatus.FAILED
        assert cmd.error_message == "Vehicle is moving"
        assert cmd.response_time is None
    
    def test_mark_timeout(self):
        """Test marking command as timed out."""
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        
        cmd.mark_timeout(timeout_ms=5000)
        
        assert cmd.status == CommandStatus.TIMEOUT
        assert cmd.response_time == 5000
        assert "timed out after 5000ms" in cmd.error_message
    
    def test_to_dict(self):
        """Test converting command to dictionary."""
        cmd = RemoteCommand(
            command_type=CommandType.SEAT_HEAT,
            parameters={'seat': 'front_left', 'level': 'high'}
        )
        cmd.mark_success(1200)
        
        data = cmd.to_dict()
        
        assert data['command_type'] == 'seat_heat'
        assert data['status'] == 'success'
        assert data['parameters'] == {'seat': 'front_left', 'level': 'high'}
        assert data['response_time'] == 1200
        assert data['error_message'] is None
        assert isinstance(data['command_id'], str)
        assert isinstance(data['timestamp'], str)
    
    def test_from_dict(self):
        """Test creating command from dictionary."""
        data = {
            'command_id': '550e8400-e29b-41d4-a716-446655440000',
            'command_type': 'climate_on',
            'parameters': {'target_temp': 22.0},
            'status': 'success',
            'timestamp': '2025-12-07T10:30:00',
            'response_time': 2345,
            'error_message': None
        }
        
        cmd = RemoteCommand.from_dict(data)
        
        assert cmd.command_id == UUID('550e8400-e29b-41d4-a716-446655440000')
        assert cmd.command_type == CommandType.CLIMATE_ON
        assert cmd.parameters == {'target_temp': 22.0}
        assert cmd.status == CommandStatus.SUCCESS
        assert cmd.response_time == 2345
        assert cmd.error_message is None
    
    def test_round_trip_serialization(self):
        """Test command can be serialized and deserialized."""
        original = RemoteCommand(
            command_type=CommandType.HONK_FLASH,
            parameters={'duration': 3}
        )
        original.mark_success(890)
        
        data = original.to_dict()
        restored = RemoteCommand.from_dict(data)
        
        assert restored.command_id == original.command_id
        assert restored.command_type == original.command_type
        assert restored.parameters == original.parameters
        assert restored.status == original.status
        assert restored.response_time == original.response_time
        assert restored.error_message == original.error_message
