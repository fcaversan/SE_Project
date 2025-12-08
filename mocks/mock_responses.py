"""
Mock vehicle data responses and scenarios.

Per research.md: Provides various mock data scenarios for testing.
"""

from datetime import datetime, timedelta
from models.vehicle_state import VehicleState
from models.enums import LockStatus


def get_normal_scenario() -> VehicleState:
    """Normal operation: Charged battery, locked, comfortable temp."""
    return VehicleState(
        battery_soc=82.0,
        estimated_range_km=350.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now(),
        lock_timestamp=datetime.now() - timedelta(hours=2)
    )


def get_low_battery_scenario() -> VehicleState:
    """Low battery warning scenario."""
    return VehicleState(
        battery_soc=18.0,
        estimated_range_km=75.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=21.0,
        climate_on=False,
        last_updated=datetime.now(),
        lock_timestamp=datetime.now() - timedelta(hours=1)
    )


def get_critical_battery_scenario() -> VehicleState:
    """Critical battery warning scenario."""
    return VehicleState(
        battery_soc=3.0,
        estimated_range_km=12.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=20.0,
        climate_on=False,
        last_updated=datetime.now(),
        lock_timestamp=datetime.now() - timedelta(hours=3)
    )


def get_unlocked_scenario() -> VehicleState:
    """Vehicle unlocked recently."""
    return VehicleState(
        battery_soc=65.0,
        estimated_range_km=280.0,
        lock_status=LockStatus.UNLOCKED,
        cabin_temp_celsius=23.0,
        climate_on=False,
        last_updated=datetime.now(),
        lock_timestamp=datetime.now() - timedelta(minutes=2)
    )


def get_unlocked_too_long_scenario() -> VehicleState:
    """Vehicle unlocked for prolonged period (security warning)."""
    return VehicleState(
        battery_soc=70.0,
        estimated_range_km=295.0,
        lock_status=LockStatus.UNLOCKED,
        cabin_temp_celsius=24.0,
        climate_on=False,
        last_updated=datetime.now(),
        lock_timestamp=datetime.now() - timedelta(minutes=15)
    )


def get_climate_active_scenario() -> VehicleState:
    """Climate control actively running."""
    return VehicleState(
        battery_soc=55.0,
        estimated_range_km=230.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=18.0,
        climate_on=True,
        last_updated=datetime.now(),
        lock_timestamp=datetime.now() - timedelta(hours=4)
    )


def get_stale_data_scenario() -> VehicleState:
    """Stale data (> 60 seconds old)."""
    return VehicleState(
        battery_soc=75.0,
        estimated_range_km=320.0,
        lock_status=LockStatus.LOCKED,
        cabin_temp_celsius=22.0,
        climate_on=False,
        last_updated=datetime.now() - timedelta(seconds=90),
        lock_timestamp=datetime.now() - timedelta(hours=1)
    )


# Scenario mapping for easy access
SCENARIOS = {
    'normal': get_normal_scenario,
    'low_battery': get_low_battery_scenario,
    'critical_battery': get_critical_battery_scenario,
    'unlocked': get_unlocked_scenario,
    'unlocked_too_long': get_unlocked_too_long_scenario,
    'climate_active': get_climate_active_scenario,
    'stale_data': get_stale_data_scenario,
}
