"""
Navigation service for route planning and trip management.

Handles route calculation, charging stop optimization, and energy estimation.
"""

import math
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from models.destination import Destination
from models.route import Route, ChargingStop
from models.charging_station import ChargingStation
from models.vehicle_state import VehicleState
from models.trip_history import TripHistory


class NavigationService:
    """
    Service for calculating routes and managing navigation.
    
    Implements FR-TRP-001 through FR-TRP-004.
    """
    
    # Constants for energy consumption calculation
    BASE_CONSUMPTION_KWH_PER_100KM = 18.0  # Average consumption
    BATTERY_CAPACITY_KWH = 75.0  # Total battery capacity
    MIN_CHARGING_STOP_SOC = 10.0  # Minimum SoC before stopping to charge
    TARGET_CHARGING_STOP_SOC = 80.0  # Target SoC after charging stop
    CHARGING_EFFICIENCY = 0.9  # Charging efficiency factor
    
    def __init__(self, charging_stations: List[ChargingStation]):
        """
        Initialize navigation service.
        
        Args:
            charging_stations: List of available charging stations
        """
        self.charging_stations = charging_stations
    
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        
        Args:
            lat1: Origin latitude
            lon1: Origin longitude
            lat2: Destination latitude
            lon2: Destination longitude
            
        Returns:
            Distance in kilometers
        """
        # Earth's radius in kilometers
        R = 6371.0
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c
        return round(distance, 2)
    
    def estimate_energy_consumption(self, distance_km: float, 
                                   elevation_gain_m: float = 0) -> float:
        """
        Estimate energy consumption for a route (FR-TRP-003).
        
        Args:
            distance_km: Route distance
            elevation_gain_m: Total elevation gain (increases consumption)
            
        Returns:
            Estimated energy consumption in kWh
        """
        # Base consumption
        base_energy = (distance_km / 100) * self.BASE_CONSUMPTION_KWH_PER_100KM
        
        # Add elevation penalty (roughly 0.01 kWh per 10m elevation gain)
        elevation_penalty = (elevation_gain_m / 10) * 0.01
        
        total_energy = base_energy + elevation_penalty
        return round(total_energy, 2)
    
    def calculate_route(self, origin: Destination, destination: Destination,
                       current_soc: float, elevation_gain_m: float = 0) -> Route:
        """
        Calculate route with charging stops if needed (FR-TRP-002, FR-TRP-003).
        
        Args:
            origin: Starting location
            destination: End location
            current_soc: Current state of charge (percentage)
            elevation_gain_m: Total elevation gain along route
            
        Returns:
            Route object with charging stops if needed
        """
        # Calculate straight-line distance (in production, use mapping API)
        distance_km = self.calculate_distance(
            origin.latitude, origin.longitude,
            destination.latitude, destination.longitude
        )
        
        # Estimate driving time (assuming 80 km/h average)
        duration_minutes = int((distance_km / 80) * 60)
        
        # Estimate energy consumption
        estimated_energy_kwh = self.estimate_energy_consumption(distance_km, elevation_gain_m)
        
        # Calculate current energy available
        current_energy_kwh = (current_soc / 100) * self.BATTERY_CAPACITY_KWH
        
        # Calculate arrival SoC if we drive without charging
        energy_remaining = current_energy_kwh - estimated_energy_kwh
        arrival_soc = (energy_remaining / self.BATTERY_CAPACITY_KWH) * 100
        
        # Determine if we need charging stops
        charging_stops = []
        if arrival_soc < self.MIN_CHARGING_STOP_SOC:
            charging_stops = self._plan_charging_stops(
                origin, destination, distance_km, 
                current_soc, estimated_energy_kwh
            )
            
            # Recalculate arrival SoC with charging stops
            if charging_stops:
                last_stop = charging_stops[-1]
                remaining_distance = distance_km - last_stop.distance_from_start_km
                remaining_energy = self.estimate_energy_consumption(remaining_distance)
                arrival_energy = (last_stop.departure_soc / 100) * self.BATTERY_CAPACITY_KWH - remaining_energy
                arrival_soc = (arrival_energy / self.BATTERY_CAPACITY_KWH) * 100
        
        # Ensure arrival_soc is within valid range
        arrival_soc = max(0, min(100, arrival_soc))
        
        return Route(
            origin=origin,
            destination=destination,
            distance_km=distance_km,
            duration_minutes=duration_minutes,
            estimated_energy_kwh=estimated_energy_kwh,
            arrival_soc=round(arrival_soc, 1),
            charging_stops=charging_stops
        )
    
    def _plan_charging_stops(self, origin: Destination, destination: Destination,
                            total_distance_km: float, current_soc: float,
                            total_energy_kwh: float) -> List[ChargingStop]:
        """
        Plan optimal charging stops along route.
        
        Args:
            origin: Route origin
            destination: Route destination
            total_distance_km: Total route distance
            current_soc: Starting SoC
            total_energy_kwh: Total energy needed
            
        Returns:
            List of charging stops
        """
        stops = []
        current_energy = (current_soc / 100) * self.BATTERY_CAPACITY_KWH
        distance_covered = 0
        
        # Find charging stations along the route
        route_stations = self._find_stations_along_route(origin, destination)
        
        for station in route_stations:
            # Calculate distance to this station
            station_distance = self.calculate_distance(
                origin.latitude, origin.longitude,
                station.latitude, station.longitude
            )
            
            # Skip if we've already passed this station
            if station_distance <= distance_covered:
                continue
            
            # Calculate energy to reach this station
            segment_distance = station_distance - distance_covered
            segment_energy = self.estimate_energy_consumption(segment_distance)
            
            # Check if we need to charge here
            energy_at_station = current_energy - segment_energy
            soc_at_station = (energy_at_station / self.BATTERY_CAPACITY_KWH) * 100
            
            if soc_at_station <= self.MIN_CHARGING_STOP_SOC:
                # Need to charge here
                target_energy = (self.TARGET_CHARGING_STOP_SOC / 100) * self.BATTERY_CAPACITY_KWH
                energy_to_add = target_energy - energy_at_station
                
                # Calculate charging time (simplified)
                charging_time = int((energy_to_add / (station.max_power_kw * self.CHARGING_EFFICIENCY)) * 60)
                
                stops.append(ChargingStop(
                    station=station,
                    arrival_soc=round(soc_at_station, 1),
                    departure_soc=self.TARGET_CHARGING_STOP_SOC,
                    charging_time_minutes=charging_time,
                    distance_from_start_km=station_distance
                ))
                
                # Update for next segment
                current_energy = target_energy
                distance_covered = station_distance
                
                # Check if we can reach destination from here
                remaining_distance = total_distance_km - distance_covered
                remaining_energy = self.estimate_energy_consumption(remaining_distance)
                if current_energy - remaining_energy > (self.MIN_CHARGING_STOP_SOC / 100) * self.BATTERY_CAPACITY_KWH:
                    break
        
        return stops
    
    def _find_stations_along_route(self, origin: Destination, 
                                   destination: Destination) -> List[ChargingStation]:
        """
        Find charging stations along the route (simplified).
        
        In production, this would use a proper routing API to find
        stations actually along the road path.
        
        Args:
            origin: Route origin
            destination: Route destination
            
        Returns:
            List of stations sorted by distance from origin
        """
        # Calculate distances to all stations
        stations_with_distance = []
        for station in self.charging_stations:
            distance = self.calculate_distance(
                origin.latitude, origin.longitude,
                station.latitude, station.longitude
            )
            stations_with_distance.append((station, distance))
        
        # Sort by distance and return stations
        stations_with_distance.sort(key=lambda x: x[1])
        return [station for station, _ in stations_with_distance]
    
    def search_destinations(self, query: str) -> List[Destination]:
        """
        Search for destinations by name (FR-TRP-001).
        
        In production, this would use Google Places API or similar.
        For now, returns mock results.
        
        Args:
            query: Search query
            
        Returns:
            List of matching destinations
        """
        # Mock destinations for demonstration
        mock_destinations = [
            Destination(
                name="San Francisco, CA",
                address="San Francisco, California, USA",
                latitude=37.7749,
                longitude=-122.4194,
                place_id="ChIJIQBpAG2ahYAR_6128GcTUEo"
            ),
            Destination(
                name="Los Angeles, CA",
                address="Los Angeles, California, USA",
                latitude=34.0522,
                longitude=-118.2437,
                place_id="ChIJE9on3F3HwoAR9AhGJW_fL-I"
            ),
            Destination(
                name="San Diego, CA",
                address="San Diego, California, USA",
                latitude=32.7157,
                longitude=-117.1611,
                place_id="ChIJSx6SrQ9T2YARed8V_f0hOg0"
            ),
            Destination(
                name="Seattle, WA",
                address="Seattle, Washington, USA",
                latitude=47.6062,
                longitude=-122.3321,
                place_id="ChIJVTPokywQkFQRmtVEaUZlJRA"
            )
        ]
        
        # Filter by query
        query_lower = query.lower()
        return [d for d in mock_destinations if query_lower in d.name.lower() or query_lower in d.address.lower()]
    
    def get_recent_trips(self, limit: int = 10) -> List[TripHistory]:
        """
        Get recent trip history (FR-TRP-004).
        
        In production, this would load from database.
        For now, returns mock trip data.
        
        Args:
            limit: Maximum number of trips to return
            
        Returns:
            List of recent trips
        """
        now = datetime.now()
        
        # Mock trip history
        mock_trips = [
            TripHistory(
                trip_id="trip_001",
                destination_name="San Jose, CA",
                date=now - timedelta(days=2),
                distance_km=85.3,
                duration_minutes=95,
                energy_used_kwh=15.8,
                avg_consumption=18.5,
                start_soc=95.0,
                end_soc=74.0,
                charging_stops=0
            ),
            TripHistory(
                trip_id="trip_002",
                destination_name="Sacramento, CA",
                date=now - timedelta(days=5),
                distance_km=142.5,
                duration_minutes=165,
                energy_used_kwh=26.4,
                avg_consumption=18.5,
                start_soc=100.0,
                end_soc=65.0,
                charging_stops=0
            ),
            TripHistory(
                trip_id="trip_003",
                destination_name="Monterey, CA",
                date=now - timedelta(days=8),
                distance_km=195.2,
                duration_minutes=155,
                energy_used_kwh=36.8,
                avg_consumption=18.9,
                start_soc=98.0,
                end_soc=48.0,
                charging_stops=0
            ),
            TripHistory(
                trip_id="trip_004",
                destination_name="Los Angeles, CA",
                date=now - timedelta(days=12),
                distance_km=615.8,
                duration_minutes=450,
                energy_used_kwh=115.2,
                avg_consumption=18.7,
                start_soc=100.0,
                end_soc=35.0,
                charging_stops=2
            ),
            TripHistory(
                trip_id="trip_005",
                destination_name="Lake Tahoe, CA",
                date=now - timedelta(days=18),
                distance_km=305.6,
                duration_minutes=285,
                energy_used_kwh=62.4,
                avg_consumption=20.4,  # Higher due to elevation
                start_soc=100.0,
                end_soc=17.0,
                charging_stops=1
            )
        ]
        
        return mock_trips[:limit]
