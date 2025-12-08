"""
Command queue for sequential remote command execution.

Ensures commands are executed one at a time to prevent conflicts
(e.g., simultaneous lock and unlock commands).
"""

from collections import deque
from typing import Optional, List
from uuid import UUID

from models.remote_command import RemoteCommand


class CommandQueue:
    """
    FIFO queue for sequential command execution.
    
    Maintains a queue of pending commands and ensures only one command
    executes at a time. Prevents conflicts like simultaneous lock/unlock.
    
    Thread-safe for single-threaded applications. For multi-threaded use,
    add locking mechanisms.
    """
    
    def __init__(self) -> None:
        """Initialize empty command queue."""
        self._queue: deque[RemoteCommand] = deque()
        self._executing: Optional[RemoteCommand] = None
    
    def enqueue(self, command: RemoteCommand) -> None:
        """
        Add command to the end of the queue.
        
        Args:
            command: RemoteCommand to enqueue
        """
        self._queue.append(command)
    
    def dequeue(self) -> Optional[RemoteCommand]:
        """
        Remove and return the next command from the queue.
        
        Returns:
            Next command in queue, or None if queue is empty
        """
        if self._queue:
            return self._queue.popleft()
        return None
    
    def get_pending(self) -> List[RemoteCommand]:
        """
        Get all pending commands in queue order.
        
        Does not remove commands from queue.
        
        Returns:
            List of pending commands (oldest first)
        """
        return list(self._queue)
    
    def set_executing(self, command: Optional[RemoteCommand]) -> None:
        """
        Mark a command as currently executing.
        
        Args:
            command: Command being executed, or None if execution complete
        """
        self._executing = command
    
    def get_executing(self) -> Optional[RemoteCommand]:
        """
        Get the currently executing command.
        
        Returns:
            Currently executing command, or None if queue is idle
        """
        return self._executing
    
    def is_empty(self) -> bool:
        """
        Check if queue has any pending commands.
        
        Returns:
            True if queue is empty (no pending commands)
        """
        return len(self._queue) == 0
    
    def size(self) -> int:
        """
        Get number of pending commands in queue.
        
        Returns:
            Number of commands waiting for execution
        """
        return len(self._queue)
    
    def clear(self) -> None:
        """Remove all pending commands from queue."""
        self._queue.clear()
        self._executing = None
    
    def find_by_id(self, command_id: UUID) -> Optional[RemoteCommand]:
        """
        Find a command in the queue by ID.
        
        Args:
            command_id: UUID of command to find
            
        Returns:
            Command if found in queue, None otherwise
        """
        for cmd in self._queue:
            if cmd.command_id == command_id:
                return cmd
        
        if self._executing and self._executing.command_id == command_id:
            return self._executing
        
        return None
    
    def remove_by_id(self, command_id: UUID) -> bool:
        """
        Remove a command from the queue by ID.
        
        Cannot remove currently executing command.
        
        Args:
            command_id: UUID of command to remove
            
        Returns:
            True if command was removed, False if not found or executing
        """
        if self._executing and self._executing.command_id == command_id:
            return False  # Cannot cancel executing command
        
        for i, cmd in enumerate(self._queue):
            if cmd.command_id == command_id:
                del self._queue[i]
                return True
        
        return False
