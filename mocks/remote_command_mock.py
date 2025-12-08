"""
Mock implementation of RemoteCommandService.

Simulates remote command execution with realistic delays, failures,
and state changes for development and testing without a real vehicle.
"""

import time
import random
from datetime import datetime
from typing import Optional, Dict
from uuid import UUID

from models.remote_command import RemoteCommand
from models.enums import CommandType, CommandStatus, LockStatus, SeatHeatLevel
from models.vehicle_state import VehicleState
from services.remote_command_service import RemoteCommandService
from services.command_queue import CommandQueue
from services.data_persistence import save_command_history, load_command_history


class RemoteCommandMockService(RemoteCommandService):
    """
    Mock implementation of remote command service.
    
    Simulates realistic command execution with:
    - Configurable delays (1-3 seconds typical)
    - Random failures (configurable success rate)
    - State changes in VehicleState
    - Battery drain simulation for climate commands
    - Command history persistence
    
    Attributes:
        vehicle_state: Current vehicle state to modify
        success_rate: Probability of command success (0.0-1.0)
        min_delay_ms: Minimum simulated command delay
        max_delay_ms: Maximum simulated command delay
    """
    
    def __init__(
        self,
        vehicle_state: VehicleState,
        success_rate: float = 0.95,
        min_delay_ms: int = 1000,
        max_delay_ms: int = 3000
    ) -> None:
        """
        Initialize mock service.
        
        Args:
            vehicle_state: VehicleState to modify on command execution
            success_rate: Probability of command success (default 95%)
            min_delay_ms: Minimum delay in milliseconds
            max_delay_ms: Maximum delay in milliseconds
        """
        self.vehicle_state = vehicle_state
        self.success_rate = success_rate
        self.min_delay_ms = min_delay_ms
        self.max_delay_ms = max_delay_ms
        
        self._command_queue = CommandQueue()
        self._command_history: Dict[UUID, RemoteCommand] = {}
        
        # Load persisted command history
        self._load_history()
    
    def send_command(self, command: RemoteCommand) -> RemoteCommand:
        """
        Send command for execution (simulated).
        
        Validates command, enqueues for execution, and simulates
        realistic execution with delays.
        
        Args:
            command: RemoteCommand to execute
            
        Returns:
            RemoteCommand with updated status
            
        Raises:
            ValueError: If command is invalid or vehicle state prevents execution
        """
        # Validate command before enqueuing
        self._validate_command(command)
        
        # Enqueue command
        self._command_queue.enqueue(command)
        self._command_history[command.command_id] = command
        
        # Execute immediately if no other commands pending
        if self._command_queue.size() == 1:
            self._execute_next()
        
        return command
    
    def get_command_status(self, command_id: UUID) -> Optional[RemoteCommand]:
        """
        Get status of a command by ID.
        
        Args:
            command_id: UUID of command
            
        Returns:
            RemoteCommand with current status, or None if not found
        """
        return self._command_history.get(command_id)
    
    def cancel_command(self, command_id: UUID) -> bool:
        """
        Cancel a pending command.
        
        Args:
            command_id: UUID of command to cancel
            
        Returns:
            True if cancelled, False if not found or not cancellable
        """
        return self._command_queue.remove_by_id(command_id)
    
    def _validate_command(self, command: RemoteCommand) -> None:
        """
        Validate command before execution.
        
        Args:
            command: RemoteCommand to validate
            
        Raises:
            ValueError: If command is invalid or unsafe
        """
        # Check battery level for climate commands
        if command.command_type in [CommandType.CLIMATE_ON, CommandType.SET_TEMP]:
            if self.vehicle_state.battery_soc < 10.0:
                raise ValueError("Battery too low (<10%) for climate control")
        
        # Check if already in target state for climate
        if command.command_type == CommandType.CLIMATE_ON:
            if self.vehicle_state.climate_on:
                raise ValueError("Climate control is already on")
        elif command.command_type == CommandType.CLIMATE_OFF:
            if not self.vehicle_state.climate_on:
                raise ValueError("Climate control is already off")
        
        # Check vehicle speed for trunk/frunk commands
        if command.command_type in [CommandType.TRUNK_OPEN, CommandType.FRUNK_OPEN]:
            if self.vehicle_state.speed_mph > 0:
                raise ValueError("Cannot open trunk/frunk while vehicle is moving")
        
        # Check if already in target state
        if command.command_type == CommandType.LOCK:
            if self.vehicle_state.lock_status == LockStatus.LOCKED:
                raise ValueError("Vehicle is already locked")
        elif command.command_type == CommandType.UNLOCK:
            if self.vehicle_state.lock_status == LockStatus.UNLOCKED:
                raise ValueError("Vehicle is already unlocked")
    
    def _execute_next(self) -> None:
        """Execute the next command in the queue."""
        command = self._command_queue.dequeue()
        if not command:
            return
        
        self._command_queue.set_executing(command)
        
        # Simulate execution delay
        delay_ms = random.randint(self.min_delay_ms, self.max_delay_ms)
        time.sleep(delay_ms / 1000.0)
        
        # Simulate success/failure
        if random.random() < self.success_rate:
            self._execute_command(command, delay_ms)
        else:
            command.mark_failed("Simulated failure", delay_ms)
        
        self._command_queue.set_executing(None)
        
        # Save updated history
        self._save_history()
        
        # Execute next command if queue not empty
        if not self._command_queue.is_empty():
            self._execute_next()
    
    def _execute_command(self, command: RemoteCommand, delay_ms: int) -> None:
        """
        Execute command and update vehicle state.
        
        Args:
            command: RemoteCommand to execute
            delay_ms: Simulated execution time
        """
        cmd_type = command.command_type
        
        try:
            if cmd_type == CommandType.LOCK:
                self.vehicle_state.lock_status = LockStatus.LOCKED
                self.vehicle_state.lock_timestamp = datetime.now()
            
            elif cmd_type == CommandType.UNLOCK:
                self.vehicle_state.lock_status = LockStatus.UNLOCKED
                self.vehicle_state.lock_timestamp = datetime.now()
            
            elif cmd_type == CommandType.CLIMATE_ON:
                self.vehicle_state.climate_on = True
                self.vehicle_state.climate_settings.is_active = True
                if 'target_temp' in command.parameters:
                    temp = command.parameters['target_temp']
                    self.vehicle_state.climate_settings.set_temperature(temp)
            
            elif cmd_type == CommandType.CLIMATE_OFF:
                self.vehicle_state.climate_on = False
                self.vehicle_state.climate_settings.is_active = False
            
            elif cmd_type == CommandType.SET_TEMP:
                if 'target_temp' in command.parameters:
                    temp = command.parameters['target_temp']
                    self.vehicle_state.climate_settings.set_temperature(temp)
            
            elif cmd_type == CommandType.SEAT_HEAT:
                seat = command.parameters.get('seat', 'front_left')
                level = SeatHeatLevel(command.parameters.get('level', 'off'))
                if seat == 'front_left':
                    self.vehicle_state.climate_settings.front_left_seat_heat = level
                elif seat == 'front_right':
                    self.vehicle_state.climate_settings.front_right_seat_heat = level
                elif seat == 'rear':
                    self.vehicle_state.climate_settings.rear_seat_heat = level
            
            elif cmd_type == CommandType.STEERING_HEAT:
                enabled = command.parameters.get('enabled', False)
                self.vehicle_state.climate_settings.steering_wheel_heat = enabled
            
            elif cmd_type == CommandType.DEFROST:
                position = command.parameters.get('position', 'front')
                enabled = command.parameters.get('enabled', False)
                if position == 'front':
                    self.vehicle_state.climate_settings.front_defrost = enabled
                elif position == 'rear':
                    self.vehicle_state.climate_settings.rear_defrost = enabled
            
            elif cmd_type == CommandType.TRUNK_OPEN:
                self.vehicle_state.trunk_status.rear_trunk_open = True
            
            elif cmd_type == CommandType.FRUNK_OPEN:
                self.vehicle_state.trunk_status.front_trunk_open = True
            
            elif cmd_type == CommandType.HONK_FLASH:
                # Honk and flash don't modify state, just log success
                pass
            
            # Simulate battery drain for climate operations
            if cmd_type == CommandType.CLIMATE_ON:
                drain = self.vehicle_state.climate_settings.estimate_battery_drain_per_10min(
                    self.vehicle_state.cabin_temp_celsius
                )
                # Apply 1/60th of 10-min drain per second of execution
                simulated_drain = drain * (delay_ms / 1000.0) / 600.0
                self.vehicle_state.battery_soc = max(
                    0.0,
                    self.vehicle_state.battery_soc - simulated_drain
                )
            
            # Update vehicle state timestamp
            self.vehicle_state.last_updated = datetime.now()
            
            # Mark command as successful
            command.mark_success(delay_ms)
        
        except Exception as e:
            command.mark_failed(str(e), delay_ms)
    
    def _save_history(self) -> None:
        """Persist command history to disk."""
        history_data = [cmd.to_dict() for cmd in self._command_history.values()]
        save_command_history(history_data)
    
    def _load_history(self) -> None:
        """Load command history from disk."""
        history_data = load_command_history()
        for cmd_dict in history_data:
            try:
                cmd = RemoteCommand.from_dict(cmd_dict)
                self._command_history[cmd.command_id] = cmd
            except Exception:
                # Skip invalid history entries
                pass
