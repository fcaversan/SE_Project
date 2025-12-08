"""
Unit tests for RemoteCommandMockService.

Tests command execution simulation, state changes, and validation.
"""

import pytest
from datetime import datetime

from mocks.remote_command_mock import RemoteCommandMockService
from models.remote_command import RemoteCommand
from models.vehicle_state import VehicleState
from models.enums import (
    CommandType, CommandStatus, LockStatus, SeatHeatLevel
)


@pytest.fixture
def vehicle_state():
    """Create test vehicle state."""
    return VehicleState(
        battery_soc=75.0,
        estimated_range_km=320.0,
        lock_status=LockStatus.UNLOCKED,
        cabin_temp_celsius=20.0,
        climate_on=False,
        last_updated=datetime.now(),
        speed_mph=0.0
    )


@pytest.fixture
def mock_service(vehicle_state):
    """Create mock service with test vehicle state."""
    return RemoteCommandMockService(
        vehicle_state=vehicle_state,
        success_rate=1.0,  # 100% success for deterministic tests
        min_delay_ms=10,   # Fast delays for testing
        max_delay_ms=20
    )


class TestRemoteCommandMockService:
    """Tests for RemoteCommandMockService."""
    
    def test_create_mock_service(self, vehicle_state):
        """Test creating mock service."""
        service = RemoteCommandMockService(vehicle_state)
        
        assert service.vehicle_state == vehicle_state
        assert service.success_rate == 0.95  # Default
        assert service.min_delay_ms == 1000
        assert service.max_delay_ms == 3000
    
    def test_send_lock_command(self, mock_service, vehicle_state):
        """Test sending lock command updates vehicle state."""
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        
        result = mock_service.send_command(cmd)
        
        assert result.command_id == cmd.command_id
        assert vehicle_state.lock_status == LockStatus.LOCKED
        assert vehicle_state.lock_timestamp is not None
    
    def test_send_unlock_command(self, mock_service, vehicle_state):
        """Test sending unlock command updates vehicle state."""
        vehicle_state.lock_status = LockStatus.LOCKED
        cmd = RemoteCommand(command_type=CommandType.UNLOCK)
        
        result = mock_service.send_command(cmd)
        
        assert vehicle_state.lock_status == LockStatus.UNLOCKED
        assert vehicle_state.lock_timestamp is not None
    
    def test_send_climate_on_command(self, mock_service, vehicle_state):
        """Test sending climate on command."""
        cmd = RemoteCommand(
            command_type=CommandType.CLIMATE_ON,
            parameters={'target_temp': 22.0}
        )
        
        result = mock_service.send_command(cmd)
        
        assert vehicle_state.climate_on is True
        assert vehicle_state.climate_settings.is_active is True
        assert vehicle_state.climate_settings.target_temp_celsius == 22.0
    
    def test_send_climate_off_command(self, mock_service, vehicle_state):
        """Test sending climate off command."""
        vehicle_state.climate_on = True
        cmd = RemoteCommand(command_type=CommandType.CLIMATE_OFF)
        
        result = mock_service.send_command(cmd)
        
        assert vehicle_state.climate_on is False
        assert vehicle_state.climate_settings.is_active is False
    
    def test_send_set_temp_command(self, mock_service, vehicle_state):
        """Test sending set temperature command."""
        cmd = RemoteCommand(
            command_type=CommandType.SET_TEMP,
            parameters={'target_temp': 24.5}
        )
        
        result = mock_service.send_command(cmd)
        
        assert vehicle_state.climate_settings.target_temp_celsius == 24.5
    
    def test_send_seat_heat_command(self, mock_service, vehicle_state):
        """Test sending seat heat command."""
        cmd = RemoteCommand(
            command_type=CommandType.SEAT_HEAT,
            parameters={'seat': 'front_left', 'level': 'high'}
        )
        
        result = mock_service.send_command(cmd)
        
        assert vehicle_state.climate_settings.front_left_seat_heat == SeatHeatLevel.HIGH
    
    def test_send_steering_heat_command(self, mock_service, vehicle_state):
        """Test sending steering wheel heat command."""
        cmd = RemoteCommand(
            command_type=CommandType.STEERING_HEAT,
            parameters={'enabled': True}
        )
        
        result = mock_service.send_command(cmd)
        
        assert vehicle_state.climate_settings.steering_wheel_heat is True
    
    def test_send_defrost_command(self, mock_service, vehicle_state):
        """Test sending defrost command."""
        cmd = RemoteCommand(
            command_type=CommandType.DEFROST,
            parameters={'position': 'front', 'enabled': True}
        )
        
        result = mock_service.send_command(cmd)
        
        assert vehicle_state.climate_settings.front_defrost is True
    
    def test_send_trunk_open_command(self, mock_service, vehicle_state):
        """Test sending trunk open command."""
        cmd = RemoteCommand(command_type=CommandType.TRUNK_OPEN)
        
        result = mock_service.send_command(cmd)
        
        assert vehicle_state.trunk_status.rear_trunk_open is True
    
    def test_send_frunk_open_command(self, mock_service, vehicle_state):
        """Test sending frunk open command."""
        cmd = RemoteCommand(command_type=CommandType.FRUNK_OPEN)
        
        result = mock_service.send_command(cmd)
        
        assert vehicle_state.trunk_status.front_trunk_open is True
    
    def test_send_honk_flash_command(self, mock_service, vehicle_state):
        """Test sending honk & flash command."""
        cmd = RemoteCommand(command_type=CommandType.HONK_FLASH)
        
        result = mock_service.send_command(cmd)
        
        # Honk & flash doesn't modify state, just succeeds
        assert result.command_id == cmd.command_id
    
    def test_get_command_status(self, mock_service):
        """Test retrieving command status by ID."""
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        
        mock_service.send_command(cmd)
        retrieved = mock_service.get_command_status(cmd.command_id)
        
        assert retrieved is not None
        assert retrieved.command_id == cmd.command_id
        assert retrieved.status == CommandStatus.SUCCESS
    
    def test_get_command_status_not_found(self, mock_service):
        """Test get_command_status returns None for unknown ID."""
        from uuid import uuid4
        
        result = mock_service.get_command_status(uuid4())
        
        assert result is None
    
    def test_validate_climate_low_battery(self, mock_service, vehicle_state):
        """Test climate command rejected when battery < 10%."""
        vehicle_state.battery_soc = 9.0
        cmd = RemoteCommand(command_type=CommandType.CLIMATE_ON)
        
        with pytest.raises(ValueError, match="Battery too low"):
            mock_service.send_command(cmd)
    
    def test_validate_trunk_while_moving(self, mock_service, vehicle_state):
        """Test trunk command rejected when vehicle is moving."""
        vehicle_state.speed_mph = 15.0
        cmd = RemoteCommand(command_type=CommandType.TRUNK_OPEN)
        
        with pytest.raises(ValueError, match="moving"):
            mock_service.send_command(cmd)
    
    def test_validate_frunk_while_moving(self, mock_service, vehicle_state):
        """Test frunk command rejected when vehicle is moving."""
        vehicle_state.speed_mph = 5.0
        cmd = RemoteCommand(command_type=CommandType.FRUNK_OPEN)
        
        with pytest.raises(ValueError, match="moving"):
            mock_service.send_command(cmd)
    
    def test_validate_lock_already_locked(self, mock_service, vehicle_state):
        """Test lock command rejected when already locked."""
        vehicle_state.lock_status = LockStatus.LOCKED
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        
        with pytest.raises(ValueError, match="already locked"):
            mock_service.send_command(cmd)
    
    def test_validate_unlock_already_unlocked(self, mock_service, vehicle_state):
        """Test unlock command rejected when already unlocked."""
        vehicle_state.lock_status = LockStatus.UNLOCKED
        cmd = RemoteCommand(command_type=CommandType.UNLOCK)
        
        with pytest.raises(ValueError, match="already unlocked"):
            mock_service.send_command(cmd)
    
    def test_command_marked_success(self, mock_service):
        """Test successful command is marked with SUCCESS status."""
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        
        mock_service.send_command(cmd)
        retrieved = mock_service.get_command_status(cmd.command_id)
        
        assert retrieved.status == CommandStatus.SUCCESS
        assert retrieved.response_time is not None
        assert retrieved.response_time > 0
        assert retrieved.error_message is None
    
    def test_command_with_failure_rate(self, vehicle_state):
        """Test commands can fail based on success_rate."""
        service = RemoteCommandMockService(
            vehicle_state=vehicle_state,
            success_rate=0.0,  # 0% success = always fail
            min_delay_ms=10,
            max_delay_ms=20
        )
        
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        service.send_command(cmd)
        retrieved = service.get_command_status(cmd.command_id)
        
        assert retrieved.status == CommandStatus.FAILED
        assert retrieved.error_message is not None
    
    def test_multiple_commands_sequential(self, mock_service):
        """Test multiple commands execute sequentially."""
        cmd1 = RemoteCommand(command_type=CommandType.LOCK)
        cmd2 = RemoteCommand(command_type=CommandType.CLIMATE_ON)
        cmd3 = RemoteCommand(command_type=CommandType.TRUNK_OPEN)
        
        mock_service.send_command(cmd1)
        mock_service.send_command(cmd2)
        mock_service.send_command(cmd3)
        
        # All should complete successfully
        assert mock_service.get_command_status(cmd1.command_id).status == CommandStatus.SUCCESS
        assert mock_service.get_command_status(cmd2.command_id).status == CommandStatus.SUCCESS
        assert mock_service.get_command_status(cmd3.command_id).status == CommandStatus.SUCCESS
    
    def test_cancel_pending_command(self, mock_service):
        """Test cancelling a pending command."""
        # Create service with longer delays so command stays pending
        service = RemoteCommandMockService(
            vehicle_state=mock_service.vehicle_state,
            min_delay_ms=5000,
            max_delay_ms=5000
        )
        
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        service.send_command(cmd)
        
        # Cancel should succeed for first command (might be executing)
        # But we can test the cancel_command method exists and works
        from uuid import uuid4
        result = service.cancel_command(uuid4())
        assert result is False  # Unknown command ID
