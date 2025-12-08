"""
VehicleDataService interface - defines contract for vehicle data retrieval.

Per UML class diagram: Home_Screen_Vehicle_Status_v3_class_diagram.puml
"""

from abc import ABC, abstractmethod
from models.vehicle_state import VehicleState


class VehicleDataService(ABC):
    """
    Abstract interface for vehicle data services.
    
    Implementations may be real API clients or mock services.
    """
    
    @abstractmethod
    def get_vehicle_state(self) -> VehicleState:
        """
        Retrieve current vehicle state.
        
        Returns:
            VehicleState object with current data
        
        Raises:
            Exception: If unable to retrieve vehicle data
        """
        pass
    
    @abstractmethod
    def refresh_data(self) -> VehicleState:
        """
        Force refresh of vehicle data.
        
        Returns:
            Updated VehicleState object
        
        Raises:
            Exception: If unable to refresh vehicle data
        """
        pass
