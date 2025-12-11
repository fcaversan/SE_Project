/**
 * Navigation and Trip Planning
 * Handles destination search, route calculation, and trip management
 */

class NavigationManager {
    constructor() {
        this.apiClient = new APIClient();
        this.currentRoute = null;
        this.selectedDestination = null;
        this.searchTimeout = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadCurrentLocation();
        this.loadNearbyStations();
        this.loadRecentTrips();
    }
    
    bindEvents() {
        // Destination search
        document.getElementById('destinationInput').addEventListener('input', (e) => {
            clearTimeout(this.searchTimeout);
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                this.hideSearchResults();
                return;
            }
            
            this.searchTimeout = setTimeout(() => {
                this.searchDestinations(query);
            }, 300);
        });
        
        // Calculate route button
        document.getElementById('calculateRouteBtn').addEventListener('click', () => {
            this.calculateRoute();
        });
        
        // Clear route button
        document.getElementById('clearRouteBtn').addEventListener('click', () => {
            this.clearRoute();
        });
        
        // Send to vehicle button
        document.getElementById('startNavigationBtn').addEventListener('click', () => {
            this.sendToVehicle();
        });
        
        // Click outside search results to close
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.form-group')) {
                this.hideSearchResults();
            }
        });
    }
    
    async loadCurrentLocation() {
        try {
            const response = await this.apiClient.get('/vehicle/status');
            
            if (response.success) {
                // In production, would use actual vehicle location
                document.getElementById('originInput').value = 'Current Location (Vehicle)';
            }
        } catch (error) {
            console.error('Error loading location:', error);
            document.getElementById('originInput').value = 'San Francisco, CA';
        }
    }
    
    async searchDestinations(query) {
        try {
            const response = await this.apiClient.get(`/navigation/search?q=${encodeURIComponent(query)}`);
            
            if (response.success && response.destinations) {
                this.showSearchResults(response.destinations);
            }
        } catch (error) {
            console.error('Error searching destinations:', error);
        }
    }
    
    showSearchResults(destinations) {
        const resultsContainer = document.getElementById('searchResults');
        
        if (destinations.length === 0) {
            resultsContainer.innerHTML = '<div class="search-result-item"><p>No results found</p></div>';
            resultsContainer.classList.remove('hidden');
            return;
        }
        
        resultsContainer.innerHTML = destinations.map(dest => `
            <div class="search-result-item" data-destination='${JSON.stringify(dest)}'>
                <div class="search-result-name">${dest.name}</div>
                <div class="search-result-address">${dest.address}</div>
            </div>
        `).join('');
        
        // Add click handlers
        resultsContainer.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                const dest = JSON.parse(item.getAttribute('data-destination'));
                this.selectDestination(dest);
            });
        });
        
        resultsContainer.classList.remove('hidden');
    }
    
    hideSearchResults() {
        document.getElementById('searchResults').classList.add('hidden');
    }
    
    selectDestination(destination) {
        this.selectedDestination = destination;
        document.getElementById('destinationInput').value = destination.name;
        this.hideSearchResults();
    }
    
    async calculateRoute() {
        if (!this.selectedDestination) {
            this.showToast('Please select a destination', 'error');
            return;
        }
        
        try {
            // Get current vehicle status
            const statusResponse = await this.apiClient.get('/vehicle/status');
            
            if (!statusResponse.success) {
                this.showToast('Unable to get vehicle status', 'error');
                return;
            }
            
            const currentSoC = statusResponse.data.battery_soc;
            
            // Calculate route
            const response = await this.apiClient.post('/navigation/calculate-route', {
                destination: this.selectedDestination,
                current_soc: currentSoC,
                elevation_gain_m: 0  // Would come from routing API
            });
            
            if (response.success && response.route) {
                this.currentRoute = response.route;
                this.displayRoute(response.route);
            } else {
                this.showToast(response.error || 'Failed to calculate route', 'error');
            }
        } catch (error) {
            console.error('Error calculating route:', error);
            this.showToast('Error calculating route', 'error');
        }
    }
    
    displayRoute(route) {
        // Show route card
        document.getElementById('routeCard').classList.remove('hidden');
        
        // Update route stats
        document.getElementById('routeDistance').textContent = `${route.distance_km} km`;
        document.getElementById('routeDuration').textContent = `${route.duration_minutes} min`;
        document.getElementById('routeEnergy').textContent = `${route.estimated_energy_kwh} kWh`;
        
        // Update arrival SoC with warning if low
        const arrivalSoCEl = document.getElementById('arrivalSoC');
        arrivalSoCEl.textContent = `${route.arrival_soc}%`;
        
        if (route.arrival_soc < 20) {
            arrivalSoCEl.style.color = 'var(--danger)';
        } else if (route.arrival_soc < 50) {
            arrivalSoCEl.style.color = 'var(--warning)';
        } else {
            arrivalSoCEl.style.color = 'var(--primary)';
        }
        
        // Display charging stops if needed
        if (route.needs_charging && route.charging_stops.length > 0) {
            this.displayChargingStops(route.charging_stops);
            document.getElementById('chargingStopsSection').classList.remove('hidden');
        } else {
            document.getElementById('chargingStopsSection').classList.add('hidden');
        }
        
        // Scroll to route card
        document.getElementById('routeCard').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
    
    displayChargingStops(stops) {
        const stopsListEl = document.getElementById('stopsList');
        
        stopsListEl.innerHTML = stops.map((stop, index) => `
            <div class="stop-item">
                <div class="stop-header">
                    <div class="stop-name">${stop.station.name}</div>
                    <div class="stop-number">${index + 1}</div>
                </div>
                <div class="stop-details">
                    <div class="stop-detail">
                        <span class="stop-detail-label">Arrival SoC</span>
                        <span class="stop-detail-value">${stop.arrival_soc}%</span>
                    </div>
                    <div class="stop-detail">
                        <span class="stop-detail-label">Charge To</span>
                        <span class="stop-detail-value">${stop.departure_soc}%</span>
                    </div>
                    <div class="stop-detail">
                        <span class="stop-detail-label">Charging Time</span>
                        <span class="stop-detail-value">${stop.charging_time_minutes} min</span>
                    </div>
                    <div class="stop-detail">
                        <span class="stop-detail-label">Distance</span>
                        <span class="stop-detail-value">${stop.distance_from_start_km.toFixed(1)} km</span>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    clearRoute() {
        this.currentRoute = null;
        document.getElementById('routeCard').classList.add('hidden');
        this.showToast('Route cleared', 'info');
    }
    
    async sendToVehicle() {
        if (!this.currentRoute) {
            this.showToast('No route to send', 'error');
            return;
        }
        
        try {
            const response = await this.apiClient.post('/navigation/send-to-vehicle', {
                route: this.currentRoute
            });
            
            if (response.success) {
                this.showToast('Route sent to vehicle navigation', 'success');
            } else {
                this.showToast(response.error || 'Failed to send route', 'error');
            }
        } catch (error) {
            console.error('Error sending route:', error);
            this.showToast('Error sending route to vehicle', 'error');
        }
    }
    
    async loadNearbyStations() {
        try {
            const response = await this.apiClient.get('/charging/stations');
            
            if (response.success && response.stations) {
                this.displayNearbyStations(response.stations.slice(0, 5));
            }
        } catch (error) {
            console.error('Error loading nearby stations:', error);
        }
    }
    
    displayNearbyStations(stations) {
        const listEl = document.getElementById('nearbyStationsList');
        
        if (stations.length === 0) {
            listEl.innerHTML = '<p class="empty-state">No nearby stations found</p>';
            return;
        }
        
        listEl.innerHTML = stations.map(station => `
            <div class="station-item" onclick="window.location.href='/stations'">
                <div class="station-info">
                    <h4>${station.name}</h4>
                    <p>${station.address}</p>
                </div>
                <div class="station-distance">${this.formatDistance(station.distance_km)}</div>
            </div>
        `).join('');
    }
    
    formatDistance(distanceKm) {
        if (distanceKm < 1) {
            return `${Math.round(distanceKm * 1000)} m`;
        }
        return `${distanceKm.toFixed(1)} km`;
    }
    
    async loadRecentTrips() {
        try {
            const response = await this.apiClient.get('/navigation/recent-trips?limit=5');
            
            if (response.success && response.trips) {
                this.displayRecentTrips(response.trips);
            }
        } catch (error) {
            console.error('Error loading recent trips:', error);
        }
    }
    
    displayRecentTrips(trips) {
        const listEl = document.getElementById('tripsList');
        
        if (trips.length === 0) {
            listEl.innerHTML = '<p class="empty-state">No recent trips</p>';
            return;
        }
        
        listEl.innerHTML = trips.map(trip => {
            const date = new Date(trip.date);
            const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            
            return `
                <div class="trip-item">
                    <div class="trip-header">
                        <div class="trip-destination">${trip.destination_name}</div>
                        <div class="trip-date">${dateStr}</div>
                    </div>
                    <div class="trip-stats">
                        <div class="trip-stat">
                            <span class="trip-stat-value">${trip.distance_km} km</span>
                            <span class="trip-stat-label">Distance</span>
                        </div>
                        <div class="trip-stat">
                            <span class="trip-stat-value">${trip.energy_used_kwh} kWh</span>
                            <span class="trip-stat-label">Energy</span>
                        </div>
                        <div class="trip-stat">
                            <span class="trip-stat-value">${trip.avg_consumption} kWh/100km</span>
                            <span class="trip-stat-label">Avg Consumption</span>
                        </div>
                        ${trip.charging_stops > 0 ? `
                            <div class="trip-stat">
                                <span class="trip-stat-value">${trip.charging_stops}</span>
                                <span class="trip-stat-label">Charging Stops</span>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }
    
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        
        toastMessage.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.remove('hidden');
        
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.navigationManager = new NavigationManager();
});
