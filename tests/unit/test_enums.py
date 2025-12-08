"""
Unit tests for new enums added in Remote Controls feature.

Tests CommandType, CommandStatus, and SeatHeatLevel enums.
"""

import pytest
from models.enums import CommandType, CommandStatus, SeatHeatLevel


class TestCommandType:
    """Tests for CommandType enum."""
    
    def test_all_command_types_exist(self):
        """Verify all required command types are defined."""
        assert CommandType.LOCK
        assert CommandType.UNLOCK
        assert CommandType.CLIMATE_ON
        assert CommandType.CLIMATE_OFF
        assert CommandType.SET_TEMP
        assert CommandType.SEAT_HEAT
        assert CommandType.STEERING_HEAT
        assert CommandType.DEFROST
        assert CommandType.TRUNK_OPEN
        assert CommandType.FRUNK_OPEN
        assert CommandType.HONK_FLASH
    
    def test_command_type_values(self):
        """Verify command type string values."""
        assert CommandType.LOCK.value == "lock"
        assert CommandType.UNLOCK.value == "unlock"
        assert CommandType.CLIMATE_ON.value == "climate_on"
        assert CommandType.CLIMATE_OFF.value == "climate_off"
        assert CommandType.HONK_FLASH.value == "honk_flash"
    
    def test_command_type_from_string(self):
        """Test creating CommandType from string value."""
        assert CommandType("lock") == CommandType.LOCK
        assert CommandType("climate_on") == CommandType.CLIMATE_ON
        assert CommandType("trunk_open") == CommandType.TRUNK_OPEN
    
    def test_invalid_command_type_raises_error(self):
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError):
            CommandType("invalid_command")


class TestCommandStatus:
    """Tests for CommandStatus enum."""
    
    def test_all_statuses_exist(self):
        """Verify all required statuses are defined."""
        assert CommandStatus.PENDING
        assert CommandStatus.SUCCESS
        assert CommandStatus.FAILED
        assert CommandStatus.TIMEOUT
    
    def test_status_values(self):
        """Verify status string values."""
        assert CommandStatus.PENDING.value == "pending"
        assert CommandStatus.SUCCESS.value == "success"
        assert CommandStatus.FAILED.value == "failed"
        assert CommandStatus.TIMEOUT.value == "timeout"
    
    def test_status_from_string(self):
        """Test creating CommandStatus from string value."""
        assert CommandStatus("pending") == CommandStatus.PENDING
        assert CommandStatus("success") == CommandStatus.SUCCESS
        assert CommandStatus("failed") == CommandStatus.FAILED
        assert CommandStatus("timeout") == CommandStatus.TIMEOUT
    
    def test_invalid_status_raises_error(self):
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError):
            CommandStatus("invalid_status")


class TestSeatHeatLevel:
    """Tests for SeatHeatLevel enum."""
    
    def test_all_levels_exist(self):
        """Verify all seat heat levels are defined."""
        assert SeatHeatLevel.OFF
        assert SeatHeatLevel.LOW
        assert SeatHeatLevel.MEDIUM
        assert SeatHeatLevel.HIGH
    
    def test_level_values(self):
        """Verify level string values."""
        assert SeatHeatLevel.OFF.value == "off"
        assert SeatHeatLevel.LOW.value == "low"
        assert SeatHeatLevel.MEDIUM.value == "medium"
        assert SeatHeatLevel.HIGH.value == "high"
    
    def test_level_from_string(self):
        """Test creating SeatHeatLevel from string value."""
        assert SeatHeatLevel("off") == SeatHeatLevel.OFF
        assert SeatHeatLevel("low") == SeatHeatLevel.LOW
        assert SeatHeatLevel("medium") == SeatHeatLevel.MEDIUM
        assert SeatHeatLevel("high") == SeatHeatLevel.HIGH
    
    def test_invalid_level_raises_error(self):
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError):
            SeatHeatLevel("extreme")
