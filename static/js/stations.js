/**
 * Charging Stations page JavaScript
 * Handles station search, filtering, and display
 */

class StationsManager {
    constructor() {
        this.apiClient = new APIClient();
        this.stations = [];
        this.filters = {
            distance: 10,
            connectors: ['ccs', 'chademo', 'type2'],
            minPower: 0
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadStations();
    }
    
    bindEvents() {
        // Distance slider
        const distanceSlider = document.getElementById('distanceFilter');
        distanceSlider.addEventListener('input', (e) => {
            document.getElementById('distanceValue').textContent = e.target.value + ' km';
        });
        
        // Apply filters button
        document.getElementById('applyFiltersBtn').addEventListener('click', () => {
            this.applyFilters();
        });
        
        // Reset filters button
        document.getElementById('resetFiltersBtn').addEventListener('click', () => {
            this.resetFilters();
        });
        
        // Toggle view button
        document.getElementById('toggleViewBtn').addEventListener('click', () => {
            this.toggleView();
        });
        
        // Modal controls
        document.getElementById('closeStationModalBtn').addEventListener('click', () => {
            this.hideStationModal();
        });
        
        document.getElementById('closeStationBtn').addEventListener('click', () => {
            this.hideStationModal();
        });
        
        document.getElementById('navigateBtn').addEventListener('click', () => {
            this.navigateToStation();
        });
    }
    
    async loadStations() {
        try {
            const response = await this.apiClient.get('/api/charging/stations');
            
            if (response.success) {
                this.stations = response.stations;
                this.displayStations(this.stations);
            } else {
                this.showError('Failed to load stations');
            }
        } catch (error) {
            console.error('Error loading stations:', error);
            this.showError('Error loading stations');
        }
    }
    
    applyFilters() {
        // Get filter values
        this.filters.distance = parseInt(document.getElementById('distanceFilter').value);
        this.filters.minPower = parseInt(document.getElementById('powerFilter').value);
        
        // Get selected connectors
        this.filters.connectors = [];
        document.querySelectorAll('.connector-filters input:checked').forEach(checkbox => {
            this.filters.connectors.push(checkbox.value);
        });
        
        // Build query parameters
        const params = new URLSearchParams({
            max_distance: this.filters.distance,
            min_power: this.filters.minPower
        });
        
        // Add connector types
        this.filters.connectors.forEach(connector => {
            params.append('connector_type', connector);
        });
        
        // Load filtered stations
        this.loadFilteredStations(params);
    }
    
    async loadFilteredStations(params) {
        try {
            const response = await this.apiClient.get(`/api/charging/stations?${params.toString()}`);
            
            if (response.success) {
                this.stations = response.stations;
                this.displayStations(this.stations);
                this.showToast(`Found ${this.stations.length} stations`, 'success');
            } else {
                this.showError('Failed to filter stations');
            }
        } catch (error) {
            console.error('Error filtering stations:', error);
            this.showError('Error filtering stations');
        }
    }
    
    resetFilters() {
        // Reset filter values
        document.getElementById('distanceFilter').value = 10;
        document.getElementById('distanceValue').textContent = '10 km';
        document.getElementById('powerFilter').value = 0;
        
        // Check all connector checkboxes
        document.querySelectorAll('.connector-filters input').forEach(checkbox => {
            checkbox.checked = true;
        });
        
        // Reset filters object
        this.filters = {
            distance: 10,
            connectors: ['ccs', 'chademo', 'type2'],
            minPower: 0
        };
        
        // Reload stations
        this.loadStations();
        this.showToast('Filters reset', 'success');
    }
    
    displayStations(stations) {
        const stationsList = document.getElementById('stationsList');
        const stationsCount = document.getElementById('stationsCount');
        
        stationsCount.textContent = `${stations.length} station${stations.length !== 1 ? 's' : ''}`;
        
        if (stations.length === 0) {
            stationsList.innerHTML = '<p class="empty-message">No stations found matching your filters</p>';
            return;
        }
        
        stationsList.innerHTML = stations.map(station => {
            const availableConnectors = station.available_connectors.length;
            const totalConnectors = station.total_connectors;
            const availability = availableConnectors > 0 ? 'available' : 
                (totalConnectors > 0 ? 'busy' : 'unavailable');
            
            return `
                <div class="station-card" onclick="stationsManager.showStationDetails('${station.station_id}')">
                    <div class="station-header">
                        <div class="station-info">
                            <h3>${station.name}</h3>
                            <p class="station-address">${station.address}</p>
                        </div>
                        <span class="station-distance">${station.distance_km.toFixed(1)} km</span>
                    </div>
                    
                    <div class="station-details-grid">
                        <div class="detail-item">
                            <span class="detail-label">Availability</span>
                            <div class="detail-value">
                                <span class="availability-indicator">
                                    <span class="status-dot ${availability}"></span>
                                    ${availableConnectors}/${totalConnectors} available
                                </span>
                            </div>
                        </div>
                        
                        <div class="detail-item">
                            <span class="detail-label">Power</span>
                            <span class="detail-value">${station.power_levels.join(', ')} kW</span>
                        </div>
                        
                        <div class="detail-item">
                            <span class="detail-label">Cost</span>
                            <span class="detail-value">$${station.cost_per_kwh.toFixed(2)}/kWh</span>
                        </div>
                        
                        <div class="detail-item">
                            <span class="detail-label">Connectors</span>
                            <div class="connectors-list">
                                ${station.connector_types.map(type => 
                                    `<span class="connector-badge ${type.toLowerCase()}">${type.toUpperCase()}</span>`
                                ).join('')}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    showStationDetails(stationId) {
        const station = this.stations.find(s => s.station_id === stationId);
        if (!station) return;
        
        const availableConnectors = station.available_connectors.length;
        const totalConnectors = station.total_connectors;
        const availability = availableConnectors > 0 ? 'available' : 
            (totalConnectors > 0 ? 'busy' : 'unavailable');
        
        const detailsHtml = `
            <div class="station-details-modal">
                <div class="detail-section">
                    <h4>Location</h4>
                    <div class="detail-row">
                        <span class="label">Address:</span>
                        <span class="value">${station.address}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Distance:</span>
                        <span class="value">${station.distance_km.toFixed(1)} km</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Coordinates:</span>
                        <span class="value">${station.latitude.toFixed(6)}, ${station.longitude.toFixed(6)}</span>
                    </div>
                </div>
                
                <div class="detail-section">
                    <h4>Charging</h4>
                    <div class="detail-row">
                        <span class="label">Availability:</span>
                        <span class="value">
                            <span class="availability-indicator">
                                <span class="status-dot ${availability}"></span>
                                ${availableConnectors} of ${totalConnectors} connectors available
                            </span>
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Connector Types:</span>
                        <div class="connectors-list">
                            ${station.connector_types.map(type => 
                                `<span class="connector-badge ${type.toLowerCase()}">${type.toUpperCase()}</span>`
                            ).join('')}
                        </div>
                    </div>
                    <div class="detail-row">
                        <span class="label">Power Levels:</span>
                        <span class="value">${station.power_levels.join(', ')} kW</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Cost:</span>
                        <span class="value">$${station.cost_per_kwh.toFixed(2)} per kWh</span>
                    </div>
                </div>
                
                ${station.amenities && station.amenities.length > 0 ? `
                <div class="detail-section">
                    <h4>Amenities</h4>
                    <div class="detail-row">
                        <span class="value">${station.amenities.join(', ')}</span>
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        
        document.getElementById('stationModalTitle').textContent = station.name;
        document.getElementById('stationDetails').innerHTML = detailsHtml;
        document.getElementById('stationModal').classList.remove('hidden');
        
        // Store current station for navigation
        this.currentStation = station;
    }
    
    hideStationModal() {
        document.getElementById('stationModal').classList.add('hidden');
        this.currentStation = null;
    }
    
    navigateToStation() {
        if (this.currentStation) {
            const url = `https://www.google.com/maps/dir/?api=1&destination=${this.currentStation.latitude},${this.currentStation.longitude}`;
            window.open(url, '_blank');
            this.showToast('Opening navigation in new tab', 'success');
        }
    }
    
    toggleView() {
        const mapView = document.getElementById('mapView');
        const toggleBtn = document.getElementById('toggleViewBtn');
        
        if (mapView.style.display === 'none') {
            mapView.style.display = 'flex';
            toggleBtn.textContent = 'Show List View';
        } else {
            mapView.style.display = 'none';
            toggleBtn.textContent = 'Show Map View';
        }
    }
    
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        
        toastMessage.textContent = message;
        toast.className = `toast ${type}`;
        
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }
    
    showError(message) {
        document.getElementById('stationsList').innerHTML = 
            `<p class="empty-message">${message}</p>`;
        this.showToast(message, 'error');
    }
}

// Initialize when page loads
let stationsManager;
document.addEventListener('DOMContentLoaded', () => {
    stationsManager = new StationsManager();
});
