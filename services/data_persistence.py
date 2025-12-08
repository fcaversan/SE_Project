"""
Data persistence utilities with atomic writes and file locking.

Per research.md: Implements atomic writes with file locking for JSON persistence.
"""

import json
import os
import sys
from typing import Any, Optional
from contextlib import contextmanager

# Platform-specific file locking
if sys.platform == 'win32':
    import msvcrt
    
    @contextmanager
    def file_lock(file_path: str, mode: str = 'r'):
        """
        Context manager for file locking (Windows).
        
        Args:
            file_path: Path to file to lock
            mode: File open mode ('r' or 'w')
        
        Yields:
            File handle with exclusive lock
        """
        with open(file_path, mode) as f:
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                yield f
            finally:
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl
    
    @contextmanager
    def file_lock(file_path: str, mode: str = 'r'):
        """
        Context manager for file locking (Unix).
        
        Args:
            file_path: Path to file to lock
            mode: File open mode ('r' or 'w')
        
        Yields:
            File handle with exclusive lock
        """
        with open(file_path, mode) as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                yield f
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def safe_read_json(file_path: str, default: Any = None) -> Optional[Any]:
    """
    Safely read JSON file with file locking.
    
    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is invalid
    
    Returns:
        Parsed JSON data or default value
    """
    if not os.path.exists(file_path):
        return default
    
    try:
        with file_lock(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default


def atomic_write_json(file_path: str, data: Any) -> bool:
    """
    Atomically write JSON data to file.
    
    Uses temporary file + rename for atomicity.
    
    Args:
        file_path: Path to JSON file
        data: Data to serialize to JSON
    
    Returns:
        True if successful, False otherwise
    """
    temp_path = f"{file_path}.tmp"
    
    try:
        # Write to temporary file
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Atomic rename
        os.replace(temp_path, file_path)
        return True
    except (IOError, OSError):
        # Clean up temp file on failure
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return False


def ensure_directory(file_path: str) -> None:
    """
    Ensure directory for file path exists.
    
    Args:
        file_path: Path to file (directory will be created)
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def save_command_history(commands: list, file_path: str = 'data/command_history.json') -> bool:
    """
    Save command history to JSON file.
    
    Used by RemoteCommandMockService to persist command history.
    
    Args:
        commands: List of command dictionaries
        file_path: Path to history file
    
    Returns:
        True if successful, False otherwise
    """
    ensure_directory(file_path)
    return atomic_write_json(file_path, commands)


def load_command_history(file_path: str = 'data/command_history.json') -> list:
    """
    Load command history from JSON file.
    
    Args:
        file_path: Path to history file
    
    Returns:
        List of command dictionaries, or empty list if file doesn't exist
    """
    return safe_read_json(file_path, default=[])
