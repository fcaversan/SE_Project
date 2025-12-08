"""
Remote command service interface.

Defines the abstract interface for sending and tracking remote vehicle commands.
Mock implementations provide realistic behavior for development and testing.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from models.remote_command import RemoteCommand


class RemoteCommandService(ABC):
    """
    Abstract interface for remote vehicle command execution.
    
    Implementations handle sending commands to the vehicle and tracking
    their execution status. Mock implementations simulate realistic delays
    and failures for development without a real vehicle connection.
    """
    
    @abstractmethod
    def send_command(self, command: RemoteCommand) -> RemoteCommand:
        """
        Send a command to the vehicle for execution.
        
        Command is enqueued and executed asynchronously. Use get_command_status
        to poll for completion.
        
        Args:
            command: RemoteCommand to execute
            
        Returns:
            RemoteCommand with updated status (initially PENDING)
            
        Raises:
            ValueError: If command is invalid or vehicle state prevents execution
            ConnectionError: If unable to reach vehicle
        """
        pass
    
    @abstractmethod
    def get_command_status(self, command_id: UUID) -> Optional[RemoteCommand]:
        """
        Query the status of a previously sent command.
        
        Args:
            command_id: Unique identifier of command to check
            
        Returns:
            RemoteCommand with current status, or None if not found
        """
        pass
    
    @abstractmethod
    def cancel_command(self, command_id: UUID) -> bool:
        """
        Attempt to cancel a pending command.
        
        Only PENDING commands can be cancelled. Commands that are already
        executing or completed cannot be cancelled.
        
        Args:
            command_id: Unique identifier of command to cancel
            
        Returns:
            True if command was cancelled, False if not found or not cancellable
        """
        pass
