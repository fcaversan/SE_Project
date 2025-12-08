"""
Unit tests for TrunkStatus model.

Tests trunk status tracking and serialization.
"""

import pytest
from models.trunk_status import TrunkStatus


class TestTrunkStatus:
    """Tests for TrunkStatus model."""
    
    def test_create_with_defaults(self):
        """Test creating status with default values."""
        status = TrunkStatus()
        
        assert status.front_trunk_open is False
        assert status.rear_trunk_open is False
    
    def test_create_with_custom_values(self):
        """Test creating status with custom values."""
        status = TrunkStatus(front_trunk_open=True, rear_trunk_open=False)
        
        assert status.front_trunk_open is True
        assert status.rear_trunk_open is False
    
    def test_any_open_both_closed(self):
        """Test any_open returns False when all closed."""
        status = TrunkStatus(front_trunk_open=False, rear_trunk_open=False)
        
        assert status.any_open() is False
    
    def test_any_open_front_open(self):
        """Test any_open returns True when front trunk open."""
        status = TrunkStatus(front_trunk_open=True, rear_trunk_open=False)
        
        assert status.any_open() is True
    
    def test_any_open_rear_open(self):
        """Test any_open returns True when rear trunk open."""
        status = TrunkStatus(front_trunk_open=False, rear_trunk_open=True)
        
        assert status.any_open() is True
    
    def test_any_open_both_open(self):
        """Test any_open returns True when both trunks open."""
        status = TrunkStatus(front_trunk_open=True, rear_trunk_open=True)
        
        assert status.any_open() is True
    
    def test_all_closed_both_closed(self):
        """Test all_closed returns True when all closed."""
        status = TrunkStatus(front_trunk_open=False, rear_trunk_open=False)
        
        assert status.all_closed() is True
    
    def test_all_closed_one_open(self):
        """Test all_closed returns False when any trunk open."""
        status = TrunkStatus(front_trunk_open=True, rear_trunk_open=False)
        
        assert status.all_closed() is False
    
    def test_to_dict(self):
        """Test converting status to dictionary."""
        status = TrunkStatus(front_trunk_open=True, rear_trunk_open=False)
        
        data = status.to_dict()
        
        assert data['front_trunk_open'] is True
        assert data['rear_trunk_open'] is False
    
    def test_from_dict(self):
        """Test creating status from dictionary."""
        data = {
            'front_trunk_open': False,
            'rear_trunk_open': True
        }
        
        status = TrunkStatus.from_dict(data)
        
        assert status.front_trunk_open is False
        assert status.rear_trunk_open is True
    
    def test_from_dict_with_defaults(self):
        """Test from_dict handles missing keys with defaults."""
        data = {}
        
        status = TrunkStatus.from_dict(data)
        
        assert status.front_trunk_open is False
        assert status.rear_trunk_open is False
    
    def test_round_trip_serialization(self):
        """Test status can be serialized and deserialized."""
        original = TrunkStatus(front_trunk_open=True, rear_trunk_open=True)
        
        data = original.to_dict()
        restored = TrunkStatus.from_dict(data)
        
        assert restored.front_trunk_open == original.front_trunk_open
        assert restored.rear_trunk_open == original.rear_trunk_open
