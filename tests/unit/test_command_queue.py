"""
Unit tests for CommandQueue.

Tests queue operations, command ordering, and cancellation.
"""

import pytest
from uuid import UUID

from services.command_queue import CommandQueue
from models.remote_command import RemoteCommand
from models.enums import CommandType


class TestCommandQueue:
    """Tests for CommandQueue."""
    
    def test_create_empty_queue(self):
        """Test creating empty queue."""
        queue = CommandQueue()
        
        assert queue.is_empty() is True
        assert queue.size() == 0
        assert queue.get_executing() is None
    
    def test_enqueue_command(self):
        """Test adding command to queue."""
        queue = CommandQueue()
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        
        queue.enqueue(cmd)
        
        assert queue.is_empty() is False
        assert queue.size() == 1
    
    def test_enqueue_multiple_commands(self):
        """Test adding multiple commands."""
        queue = CommandQueue()
        cmd1 = RemoteCommand(command_type=CommandType.LOCK)
        cmd2 = RemoteCommand(command_type=CommandType.CLIMATE_ON)
        cmd3 = RemoteCommand(command_type=CommandType.TRUNK_OPEN)
        
        queue.enqueue(cmd1)
        queue.enqueue(cmd2)
        queue.enqueue(cmd3)
        
        assert queue.size() == 3
    
    def test_dequeue_command(self):
        """Test removing command from queue (FIFO)."""
        queue = CommandQueue()
        cmd1 = RemoteCommand(command_type=CommandType.LOCK)
        cmd2 = RemoteCommand(command_type=CommandType.UNLOCK)
        
        queue.enqueue(cmd1)
        queue.enqueue(cmd2)
        
        result = queue.dequeue()
        
        assert result == cmd1  # First in, first out
        assert queue.size() == 1
    
    def test_dequeue_empty_queue(self):
        """Test dequeue on empty queue returns None."""
        queue = CommandQueue()
        
        result = queue.dequeue()
        
        assert result is None
    
    def test_fifo_ordering(self):
        """Test commands are dequeued in FIFO order."""
        queue = CommandQueue()
        cmd1 = RemoteCommand(command_type=CommandType.LOCK)
        cmd2 = RemoteCommand(command_type=CommandType.UNLOCK)
        cmd3 = RemoteCommand(command_type=CommandType.CLIMATE_ON)
        
        queue.enqueue(cmd1)
        queue.enqueue(cmd2)
        queue.enqueue(cmd3)
        
        assert queue.dequeue() == cmd1
        assert queue.dequeue() == cmd2
        assert queue.dequeue() == cmd3
        assert queue.dequeue() is None
    
    def test_get_pending(self):
        """Test getting list of pending commands."""
        queue = CommandQueue()
        cmd1 = RemoteCommand(command_type=CommandType.LOCK)
        cmd2 = RemoteCommand(command_type=CommandType.UNLOCK)
        
        queue.enqueue(cmd1)
        queue.enqueue(cmd2)
        
        pending = queue.get_pending()
        
        assert len(pending) == 2
        assert pending[0] == cmd1
        assert pending[1] == cmd2
        # get_pending doesn't remove commands
        assert queue.size() == 2
    
    def test_set_and_get_executing(self):
        """Test tracking currently executing command."""
        queue = CommandQueue()
        cmd = RemoteCommand(command_type=CommandType.CLIMATE_ON)
        
        queue.set_executing(cmd)
        
        assert queue.get_executing() == cmd
    
    def test_clear_executing(self):
        """Test clearing executing command."""
        queue = CommandQueue()
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        
        queue.set_executing(cmd)
        queue.set_executing(None)
        
        assert queue.get_executing() is None
    
    def test_clear_queue(self):
        """Test clearing all commands from queue."""
        queue = CommandQueue()
        cmd1 = RemoteCommand(command_type=CommandType.LOCK)
        cmd2 = RemoteCommand(command_type=CommandType.UNLOCK)
        
        queue.enqueue(cmd1)
        queue.enqueue(cmd2)
        queue.set_executing(cmd1)
        
        queue.clear()
        
        assert queue.is_empty() is True
        assert queue.size() == 0
        assert queue.get_executing() is None
    
    def test_find_by_id_in_queue(self):
        """Test finding command in queue by ID."""
        queue = CommandQueue()
        cmd1 = RemoteCommand(command_type=CommandType.LOCK)
        cmd2 = RemoteCommand(command_type=CommandType.UNLOCK)
        
        queue.enqueue(cmd1)
        queue.enqueue(cmd2)
        
        found = queue.find_by_id(cmd2.command_id)
        
        assert found == cmd2
    
    def test_find_by_id_executing(self):
        """Test finding currently executing command by ID."""
        queue = CommandQueue()
        cmd = RemoteCommand(command_type=CommandType.CLIMATE_ON)
        
        queue.set_executing(cmd)
        
        found = queue.find_by_id(cmd.command_id)
        
        assert found == cmd
    
    def test_find_by_id_not_found(self):
        """Test find_by_id returns None if command not in queue."""
        queue = CommandQueue()
        
        found = queue.find_by_id(UUID('550e8400-e29b-41d4-a716-446655440000'))
        
        assert found is None
    
    def test_remove_by_id_in_queue(self):
        """Test removing command from queue by ID."""
        queue = CommandQueue()
        cmd1 = RemoteCommand(command_type=CommandType.LOCK)
        cmd2 = RemoteCommand(command_type=CommandType.UNLOCK)
        cmd3 = RemoteCommand(command_type=CommandType.CLIMATE_ON)
        
        queue.enqueue(cmd1)
        queue.enqueue(cmd2)
        queue.enqueue(cmd3)
        
        result = queue.remove_by_id(cmd2.command_id)
        
        assert result is True
        assert queue.size() == 2
        assert cmd2 not in queue.get_pending()
    
    def test_remove_by_id_not_found(self):
        """Test remove_by_id returns False if command not in queue."""
        queue = CommandQueue()
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        
        queue.enqueue(cmd)
        
        result = queue.remove_by_id(UUID('550e8400-e29b-41d4-a716-446655440000'))
        
        assert result is False
        assert queue.size() == 1
    
    def test_cannot_remove_executing_command(self):
        """Test cannot remove currently executing command."""
        queue = CommandQueue()
        cmd = RemoteCommand(command_type=CommandType.LOCK)
        
        queue.set_executing(cmd)
        
        result = queue.remove_by_id(cmd.command_id)
        
        assert result is False
        assert queue.get_executing() == cmd
