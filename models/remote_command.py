"""
Remote command model for vehicle control operations.

Represents a single remote command (lock, unlock, climate, etc.) with
execution status, timing, and error tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from models.enums import CommandType, CommandStatus


@dataclass
class RemoteCommand:
    """
    Remote command for vehicle control.
    
    Tracks command execution from initiation through completion or failure.
    Includes timing metrics and error details for debugging and UX feedback.
    
    Attributes:
        command_id: Unique identifier for command tracking
        command_type: Type of command (LOCK, UNLOCK, CLIMATE_ON, etc.)
        parameters: Command-specific parameters (e.g., target_temp for SET_TEMP)
        status: Current execution status (PENDING, SUCCESS, FAILED, TIMEOUT)
        timestamp: When command was created
        response_time: Milliseconds from initiation to completion (None if pending)
        error_message: Human-readable error description (None if successful)
    """
    
    command_type: CommandType
    parameters: Dict[str, Any] = field(default_factory=dict)
    command_id: UUID = field(default_factory=uuid4)
    status: CommandStatus = CommandStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    response_time: Optional[int] = None
    error_message: Optional[str] = None
    
    def mark_success(self, response_time_ms: int) -> None:
        """
        Mark command as successfully executed.
        
        Args:
            response_time_ms: Execution time in milliseconds
        """
        self.status = CommandStatus.SUCCESS
        self.response_time = response_time_ms
        self.error_message = None
    
    def mark_failed(self, error_message: str, response_time_ms: Optional[int] = None) -> None:
        """
        Mark command as failed with error details.
        
        Args:
            error_message: Human-readable error description
            response_time_ms: Execution time before failure (optional)
        """
        self.status = CommandStatus.FAILED
        self.error_message = error_message
        if response_time_ms is not None:
            self.response_time = response_time_ms
    
    def mark_timeout(self, timeout_ms: int) -> None:
        """
        Mark command as timed out.
        
        Args:
            timeout_ms: Timeout threshold that was exceeded
        """
        self.status = CommandStatus.TIMEOUT
        self.response_time = timeout_ms
        self.error_message = f"Command timed out after {timeout_ms}ms"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert command to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation with all fields
        """
        return {
            'command_id': str(self.command_id),
            'command_type': self.command_type.value,
            'parameters': self.parameters,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'response_time': self.response_time,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RemoteCommand':
        """
        Create command from dictionary (e.g., loaded from JSON).
        
        Args:
            data: Dictionary with command fields
            
        Returns:
            RemoteCommand instance
        """
        return cls(
            command_id=UUID(data['command_id']),
            command_type=CommandType(data['command_type']),
            parameters=data.get('parameters', {}),
            status=CommandStatus(data['status']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            response_time=data.get('response_time'),
            error_message=data.get('error_message')
        )
