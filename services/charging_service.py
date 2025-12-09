"""
Abstract base class for charging service.

Defines interface for charging operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from models.charging_session import ChargingSession
from models.charging_schedule import ChargingSchedule
from models.charging_station import ChargingStation


class ChargingService(ABC):
    """Abstract interface for charging operations."""
    
    @abstractmethod
    def start_charging(self, target_soc: int) -> ChargingSession:
        """
        Start a charging session.
        
        Args:
            target_soc: Target state of charge percentage
            
        Returns:
            ChargingSession object
            
        Raises:
            ValueError: If vehicle not plugged in or already charging
        """
        pass
    
    @abstractmethod
    def stop_charging(self) -> ChargingSession:
        """
        Stop the active charging session.
        
        Returns:
            Completed ChargingSession object
            
        Raises:
            ValueError: If not currently charging
        """
        pass
    
    @abstractmethod
    def get_current_session(self) -> Optional[ChargingSession]:
        """
        Get the current active charging session.
        
        Returns:
            ChargingSession if charging, None otherwise
        """
        pass
    
    @abstractmethod
    def get_charging_history(self, limit: int = 10) -> List[ChargingSession]:
        """
        Get historical charging sessions.
        
        Args:
            limit: Maximum number of sessions to return
            
        Returns:
            List of ChargingSession objects
        """
        pass
    
    @abstractmethod
    def get_charge_limit(self) -> int:
        """
        Get the current charge limit setting.
        
        Returns:
            Charge limit percentage (1-100)
        """
        pass
    
    @abstractmethod
    def set_charge_limit(self, limit: int) -> int:
        """
        Set the charge limit.
        
        Args:
            limit: Charge limit percentage (1-100)
            
        Returns:
            Updated charge limit
            
        Raises:
            ValueError: If limit out of range
        """
        pass
    
    @abstractmethod
    def get_schedules(self) -> List[ChargingSchedule]:
        """
        Get all charging schedules.
        
        Returns:
            List of ChargingSchedule objects
        """
        pass
    
    @abstractmethod
    def create_schedule(self, schedule: ChargingSchedule) -> ChargingSchedule:
        """
        Create a new charging schedule.
        
        Args:
            schedule: ChargingSchedule to create
            
        Returns:
            Created ChargingSchedule with ID
        """
        pass
    
    @abstractmethod
    def update_schedule(self, schedule: ChargingSchedule) -> ChargingSchedule:
        """
        Update an existing charging schedule.
        
        Args:
            schedule: ChargingSchedule with updates
            
        Returns:
            Updated ChargingSchedule
            
        Raises:
            ValueError: If schedule not found
        """
        pass
    
    @abstractmethod
    def delete_schedule(self, schedule_id: str) -> bool:
        """
        Delete a charging schedule.
        
        Args:
            schedule_id: ID of schedule to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def get_nearby_stations(
        self, 
        max_distance_km: float = 10.0,
        connector_filter: Optional[List[str]] = None,
        power_filter: Optional[int] = None
    ) -> List[ChargingStation]:
        """
        Get nearby charging stations.
        
        Args:
            max_distance_km: Maximum distance from vehicle
            connector_filter: Filter by connector types
            power_filter: Minimum power level (kW)
            
        Returns:
            List of ChargingStation objects
        """
        pass
