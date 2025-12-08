"""
Trunk status model for vehicle storage compartments.

Tracks open/closed state of front trunk (frunk) and rear trunk.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TrunkStatus:
    """
    Status of vehicle storage compartments.
    
    Tracks whether front trunk (frunk) and rear trunk are open or closed.
    
    Attributes:
        front_trunk_open: Whether front trunk (frunk) is open
        rear_trunk_open: Whether rear trunk is open
    """
    
    front_trunk_open: bool = False
    rear_trunk_open: bool = False
    
    def any_open(self) -> bool:
        """
        Check if any trunk is open.
        
        Returns:
            True if front or rear trunk is open
        """
        return self.front_trunk_open or self.rear_trunk_open
    
    def all_closed(self) -> bool:
        """
        Check if all trunks are closed.
        
        Returns:
            True if both trunks are closed
        """
        return not self.any_open()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert status to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation with all fields
        """
        return {
            'front_trunk_open': self.front_trunk_open,
            'rear_trunk_open': self.rear_trunk_open
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrunkStatus':
        """
        Create status from dictionary (e.g., loaded from JSON).
        
        Args:
            data: Dictionary with trunk status fields
            
        Returns:
            TrunkStatus instance
        """
        return cls(
            front_trunk_open=data.get('front_trunk_open', False),
            rear_trunk_open=data.get('rear_trunk_open', False)
        )
