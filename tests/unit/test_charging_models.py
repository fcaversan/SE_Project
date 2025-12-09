"""
Unit tests for charging-related data models.

Tests ChargingSession, ChargingSchedule, and ChargingStation models.
"""

import pytest
from datetime import datetime
from models.charging_session import ChargingSession
from models.charging_schedule import ChargingSchedule
from models.charging_station import ChargingStation


class TestChargingSession:
    """Tests for ChargingSession model."""
    
    def test_create_valid_session(self):
        """Test creating a valid charging session."""
        now = datetime.now()
        session = ChargingSession(
            start_time=now,
            start_soc=25.0,
            current_soc=50.0,
            target_soc=80.0,
            charging_rate_kw=150.0,
            voltage=400.0,
            amperage=375.0,
            location="Supercharger Downtown"
        )
        
        assert session.start_soc == 25.0
        assert session.current_soc == 50.0
        assert session.target_soc == 80.0
        assert session.is_active == True
        assert session.session_id is not None
    
    def test_invalid_soc_values(self):
        """Test that invalid SoC values raise ValueError."""
        now = datetime.now()
        
        with pytest.raises(ValueError, match="start_soc must be between 0 and 100"):
            ChargingSession(
                start_time=now,
                start_soc=-5.0,
                current_soc=50.0,
                target_soc=80.0,
                charging_rate_kw=150.0,
                voltage=400.0,
                amperage=375.0,
                location="Test"
            )
        
        with pytest.raises(ValueError, match="current_soc must be between 0 and 100"):
            ChargingSession(
                start_time=now,
                start_soc=25.0,
                current_soc=150.0,
                target_soc=80.0,
                charging_rate_kw=150.0,
                voltage=400.0,
                amperage=375.0,
                location="Test"
            )
    
    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        now = datetime.now()
        session = ChargingSession(
            start_time=now,
            start_soc=20.0,
            current_soc=50.0,
            target_soc=80.0,
            charging_rate_kw=150.0,
            voltage=400.0,
            amperage=375.0,
            location="Test"
        )
        
        # (50-20)/(80-20) = 30/60 = 50%
        assert session.progress_percentage() == 50.0
    
    def test_session_serialization(self):
        """Test to_dict and from_dict methods."""
        now = datetime.now()
        session = ChargingSession(
            start_time=now,
            start_soc=25.0,
            current_soc=50.0,
            target_soc=80.0,
            charging_rate_kw=150.0,
            voltage=400.0,
            amperage=375.0,
            energy_added_kwh=20.5,
            cost=7.50,
            location="Supercharger Downtown"
        )
        
        # Convert to dict
        data = session.to_dict()
        assert data['start_soc'] == 25.0
        assert data['location'] == "Supercharger Downtown"
        
        # Convert back to object
        restored = ChargingSession.from_dict(data)
        assert restored.start_soc == session.start_soc
        assert restored.location == session.location


class TestChargingSchedule:
    """Tests for ChargingSchedule model."""
    
    def test_create_valid_schedule_start_time(self):
        """Test creating schedule with start_time."""
        schedule = ChargingSchedule(
            name="Weeknight Charging",
            days_of_week=[0, 1, 2, 3, 4],  # Mon-Fri
            start_time="22:00",
            target_soc=80
        )
        
        assert schedule.name == "Weeknight Charging"
        assert schedule.start_time == "22:00"
        assert schedule.ready_by_time is None
        assert schedule.enabled == True
    
    def test_create_valid_schedule_ready_by(self):
        """Test creating schedule with ready_by_time."""
        schedule = ChargingSchedule(
            name="Morning Commute",
            days_of_week=[0, 1, 2, 3, 4],
            ready_by_time="07:00",
            target_soc=90
        )
        
        assert schedule.ready_by_time == "07:00"
        assert schedule.start_time is None
    
    def test_invalid_empty_name(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            ChargingSchedule(
                name="",
                days_of_week=[0, 1, 2],
                start_time="22:00",
                target_soc=80
            )
    
    def test_invalid_days_of_week(self):
        """Test that invalid days raise ValueError."""
        with pytest.raises(ValueError, match="days_of_week must contain values 0-6"):
            ChargingSchedule(
                name="Test",
                days_of_week=[0, 7],  # 7 is invalid
                start_time="22:00",
                target_soc=80
            )
    
    def test_invalid_target_soc(self):
        """Test that invalid target_soc raises ValueError."""
        with pytest.raises(ValueError, match="target_soc must be between 1 and 100"):
            ChargingSchedule(
                name="Test",
                days_of_week=[0, 1],
                start_time="22:00",
                target_soc=0
            )
    
    def test_both_times_set(self):
        """Test that setting both time fields raises ValueError."""
        with pytest.raises(ValueError, match="Cannot set both"):
            ChargingSchedule(
                name="Test",
                days_of_week=[0, 1],
                start_time="22:00",
                ready_by_time="07:00",
                target_soc=80
            )
    
    def test_no_times_set(self):
        """Test that setting neither time field raises ValueError."""
        with pytest.raises(ValueError, match="Must set either"):
            ChargingSchedule(
                name="Test",
                days_of_week=[0, 1],
                target_soc=80
            )
    
    def test_invalid_time_format(self):
        """Test that invalid time format raises ValueError."""
        with pytest.raises(ValueError, match="Time must be in HH:MM format"):
            ChargingSchedule(
                name="Test",
                days_of_week=[0, 1],
                start_time="25:00",  # Invalid hour
                target_soc=80
            )
    
    def test_schedule_serialization(self):
        """Test to_dict and from_dict methods."""
        schedule = ChargingSchedule(
            name="Test Schedule",
            days_of_week=[0, 1, 2],
            start_time="22:00",
            target_soc=80
        )
        
        # Convert to dict
        data = schedule.to_dict()
        assert data['name'] == "Test Schedule"
        assert data['days_of_week'] == [0, 1, 2]
        
        # Convert back to object
        restored = ChargingSchedule.from_dict(data)
        assert restored.name == schedule.name
        assert restored.days_of_week == schedule.days_of_week


class TestChargingStation:
    """Tests for ChargingStation model."""
    
    def test_create_valid_station(self):
        """Test creating a valid charging station."""
        station = ChargingStation(
            name="Supercharger Downtown",
            latitude=37.7749,
            longitude=-122.4194,
            connector_types=["tesla", "ccs"],
            power_levels_kw=[150, 250],
            total_stalls=12,
            available_stalls=8,
            cost_per_kwh=0.35
        )
        
        assert station.name == "Supercharger Downtown"
        assert station.total_stalls == 12
        assert station.available_stalls == 8
        assert station.is_operational == True
    
    def test_invalid_latitude(self):
        """Test that invalid latitude raises ValueError."""
        with pytest.raises(ValueError, match="latitude must be between"):
            ChargingStation(
                name="Test",
                latitude=100.0,  # Invalid
                longitude=-122.0,
                connector_types=["tesla"],
                power_levels_kw=[150],
                total_stalls=10,
                cost_per_kwh=0.35
            )
    
    def test_invalid_connector_type(self):
        """Test that invalid connector type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid connector type"):
            ChargingStation(
                name="Test",
                latitude=37.0,
                longitude=-122.0,
                connector_types=["invalid_type"],
                power_levels_kw=[150],
                total_stalls=10,
                cost_per_kwh=0.35
            )
    
    def test_invalid_available_stalls(self):
        """Test that invalid available_stalls raises ValueError."""
        with pytest.raises(ValueError, match="available_stalls must be between"):
            ChargingStation(
                name="Test",
                latitude=37.0,
                longitude=-122.0,
                connector_types=["tesla"],
                power_levels_kw=[150],
                total_stalls=10,
                available_stalls=15,  # More than total
                cost_per_kwh=0.35
            )
    
    def test_availability_percentage(self):
        """Test availability percentage calculation."""
        station = ChargingStation(
            name="Test",
            latitude=37.0,
            longitude=-122.0,
            connector_types=["tesla"],
            power_levels_kw=[150],
            total_stalls=10,
            available_stalls=6,
            cost_per_kwh=0.35
        )
        
        assert station.availability_percentage() == 60.0
    
    def test_max_power_kw(self):
        """Test max_power_kw method."""
        station = ChargingStation(
            name="Test",
            latitude=37.0,
            longitude=-122.0,
            connector_types=["tesla", "ccs"],
            power_levels_kw=[50, 150, 250],
            total_stalls=10,
            cost_per_kwh=0.35
        )
        
        assert station.max_power_kw() == 250
    
    def test_station_serialization(self):
        """Test to_dict and from_dict methods."""
        station = ChargingStation(
            name="Test Station",
            latitude=37.7749,
            longitude=-122.4194,
            connector_types=["tesla", "ccs"],
            power_levels_kw=[150, 250],
            total_stalls=12,
            available_stalls=8,
            cost_per_kwh=0.35,
            distance_km=2.5
        )
        
        # Convert to dict
        data = station.to_dict()
        assert data['name'] == "Test Station"
        assert data['total_stalls'] == 12
        
        # Convert back to object
        restored = ChargingStation.from_dict(data)
        assert restored.name == station.name
        assert restored.total_stalls == station.total_stalls
