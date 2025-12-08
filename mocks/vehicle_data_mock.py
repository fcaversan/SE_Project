"""
Mock implementation of VehicleDataService.

Per research.md: Class-based mock with configurable delays and failure simulation.
"""

import time
import random
from datetime import datetime
from services.vehicle_data_service import VehicleDataService
from models.vehicle_state import VehicleState
from mocks.mock_responses import SCENARIOS, get_normal_scenario


class VehicleDataMockService(VehicleDataService):
    """
    Mock vehicle data service with configurable behavior.
    
    Attributes:
        delay_seconds: Simulated network delay (default: 0.5s)
        failure_rate: Probability of failure 0.0-1.0 (default: 0.0)
        scenario: Which mock scenario to use (default: 'normal')
    """
    
    def __init__(
        self,
        delay_seconds: float = 0.5,
        failure_rate: float = 0.0,
        scenario: str = 'normal'
    ):
        """
        Initialize mock service.
        
        Args:
            delay_seconds: Simulated network delay
            failure_rate: Probability of random failure (0.0-1.0)
            scenario: Mock scenario name from SCENARIOS dict
        """
        self.delay_seconds = delay_seconds
        self.failure_rate = failure_rate
        self.scenario = scenario
        self._cached_state = None
    
    def _simulate_delay(self) -> None:
        """Simulate network latency."""
        if self.delay_seconds > 0:
            time.sleep(self.delay_seconds)
    
    def _should_fail(self) -> bool:
        """Determine if this call should simulate a failure."""
        return random.random() < self.failure_rate
    
    def get_vehicle_state(self) -> VehicleState:
        """
        Retrieve current vehicle state from mock data.
        
        Returns:
            VehicleState object
        
        Raises:
            Exception: If simulated failure occurs
        """
        self._simulate_delay()
        
        if self._should_fail():
            raise Exception("Mock failure: Unable to reach vehicle")
        
        # Return cached state if available, otherwise generate new
        if self._cached_state:
            return self._cached_state
        
        return self._get_scenario_state()
    
    def refresh_data(self) -> VehicleState:
        """
        Force refresh of vehicle data.
        
        Returns:
            Updated VehicleState object
        
        Raises:
            Exception: If simulated failure occurs
        """
        self._simulate_delay()
        
        if self._should_fail():
            raise Exception("Mock failure: Unable to refresh vehicle data")
        
        # Generate fresh state with current timestamp
        state = self._get_scenario_state()
        state.last_updated = datetime.now()
        self._cached_state = state
        return state
    
    def _get_scenario_state(self) -> VehicleState:
        """Get state for configured scenario."""
        scenario_func = SCENARIOS.get(self.scenario, get_normal_scenario)
        return scenario_func()
    
    def set_scenario(self, scenario: str) -> None:
        """
        Change mock scenario.
        
        Args:
            scenario: Scenario name from SCENARIOS dict
        """
        if scenario in SCENARIOS:
            self.scenario = scenario
            self._cached_state = None  # Clear cache
    
    def set_failure_rate(self, rate: float) -> None:
        """
        Change failure rate.
        
        Args:
            rate: Failure probability 0.0-1.0
        """
        self.failure_rate = max(0.0, min(1.0, rate))
