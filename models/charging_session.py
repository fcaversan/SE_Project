"""
Charging Session data model.

Represents a charging session with all relevant metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class ChargingSession:
    """
    Represents a vehicle charging session.
    
    Attributes:
        session_id: Unique identifier for the session
        start_time: When charging started
        end_time: When charging ended (None if active)
        start_soc: State of charge when charging started (%)
        current_soc: Current state of charge (%)
        target_soc: Target state of charge (%)
        charging_rate_kw: Current charging power (kW)
        voltage: Charging voltage (V)
        amperage: Charging current (A)
        energy_added_kwh: Total energy added (kWh)
        cost: Total cost of session ($)
        location: Charging location name
        is_active: Whether session is currently active
    """
    start_time: datetime
    start_soc: float
    current_soc: float
    target_soc: float
    charging_rate_kw: float
    voltage: float
    amperage: float
    location: str
    session_id: str = field(default_factory=lambda: str(uuid4()))
    end_time: Optional[datetime] = None
    energy_added_kwh: float = 0.0
    cost: float = 0.0
    is_active: bool = True
    
    def __post_init__(self):
        """Validate charging session data."""
        if not 0 <= self.start_soc <= 100:
            raise ValueError("start_soc must be between 0 and 100")
        if not 0 <= self.current_soc <= 100:
            raise ValueError("current_soc must be between 0 and 100")
        if not 0 <= self.target_soc <= 100:
            raise ValueError("target_soc must be between 0 and 100")
        if self.charging_rate_kw < 0:
            raise ValueError("charging_rate_kw must be non-negative")
        if self.voltage < 0:
            raise ValueError("voltage must be non-negative")
        if self.amperage < 0:
            raise ValueError("amperage must be non-negative")
    
    def progress_percentage(self) -> float:
        """Calculate charging progress as percentage."""
        if self.target_soc <= self.start_soc:
            return 100.0
        progress = (self.current_soc - self.start_soc) / (self.target_soc - self.start_soc)
        return min(100.0, max(0.0, progress * 100))
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'start_soc': self.start_soc,
            'current_soc': self.current_soc,
            'target_soc': self.target_soc,
            'charging_rate_kw': self.charging_rate_kw,
            'voltage': self.voltage,
            'amperage': self.amperage,
            'energy_added_kwh': self.energy_added_kwh,
            'cost': self.cost,
            'location': self.location,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChargingSession':
        """Create ChargingSession from dictionary."""
        return cls(
            session_id=data['session_id'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            start_soc=data['start_soc'],
            current_soc=data['current_soc'],
            target_soc=data['target_soc'],
            charging_rate_kw=data['charging_rate_kw'],
            voltage=data['voltage'],
            amperage=data['amperage'],
            energy_added_kwh=data['energy_added_kwh'],
            cost=data['cost'],
            location=data['location'],
            is_active=data['is_active']
        )
