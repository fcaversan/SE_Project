/**
 * Charging page JavaScript
 * Handles charging status, controls, and history
 */

class ChargingManager {
    constructor() {
        this.apiClient = new APIClient();
        this.currentSession = null;
        this.chargeLimit = 80;
        this.updateInterval = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadInitialData();
        
        // Start polling for status updates
        this.startStatusPolling();
    }
    
    bindEvents() {
        // Start charging button
        document.getElementById('startChargingBtn').addEventListener('click', () => {
            this.showStartModal();
        });
        
        // Stop charging button
        document.getElementById('stopChargingBtn').addEventListener('click', () => {
            this.stopCharging();
        });
        
        // Modal controls
        document.getElementById('closeModalBtn').addEventListener('click', () => {
            this.hideStartModal();
        });
        
        document.getElementById('cancelStartBtn').addEventListener('click', () => {
            this.hideStartModal();
        });
        
        document.getElementById('confirmStartBtn').addEventListener('click', () => {
            this.startCharging();
        });
        
        // Charge limit slider
        const limitSlider = document.getElementById('limitSlider');
        limitSlider.addEventListener('input', (e) => {
            document.getElementById('limitValue').textContent = e.target.value;
        });
        
        // Save limit button
        document.getElementById('saveLimitBtn').addEventListener('click', () => {
            this.saveChargeLimit();
        });
        
        // Refresh history
        document.getElementById('refreshHistoryBtn').addEventListener('click', () => {
            this.loadHistory();
        });
    }
    
    async loadInitialData() {
        try {
            // Load vehicle status for battery level
            const vehicleStatus = await this.apiClient.get('/api/vehicle/status');
            if (vehicleStatus.success) {
                const batteryLevel = Math.round(vehicleStatus.data.battery_soc);
                document.getElementById('batteryLevel').textContent = batteryLevel;
                document.getElementById('modalCurrentSoC').textContent = batteryLevel;
            }
            
            // Load charging status
            await this.updateChargingStatus();
            
            // Load charge limit
            const limitResponse = await this.apiClient.get('/api/charging/limit');
            if (limitResponse.success) {
                this.chargeLimit = limitResponse.charge_limit;
                document.getElementById('limitValue').textContent = this.chargeLimit;
                document.getElementById('limitSlider').value = this.chargeLimit;
            }
            
            // Load charging history
            await this.loadHistory();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showToast('Error loading data', 'error');
        }
    }
    
    async updateChargingStatus() {
        try {
            const response = await this.apiClient.get('/api/charging/status');
            
            if (response.success) {
                this.currentSession = response.session;
                
                if (response.is_charging && response.session) {
                    this.showChargingView(response.session);
                } else {
                    this.showNotChargingView();
                }
            }
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }
    
    showChargingView(session) {
        // Update status indicator
        const indicator = document.getElementById('chargingStatusIndicator');
        indicator.textContent = 'Charging';
        indicator.classList.add('charging');
        
        // Show/hide views
        document.getElementById('notChargingView').classList.add('hidden');
        document.getElementById('chargingView').classList.remove('hidden');
        
        // Update buttons
        document.getElementById('startChargingBtn').classList.add('hidden');
        document.getElementById('stopChargingBtn').classList.remove('hidden');
        
        // Update charging details
        const currentSoC = Math.round(session.current_soc * 10) / 10;
        const targetSoC = session.target_soc;
        const startSoC = session.start_soc;
        const progress = startSoC >= targetSoC ? 100 : 
            Math.round(((currentSoC - startSoC) / (targetSoC - startSoC)) * 100);
        
        document.getElementById('currentSoC').textContent = currentSoC;
        document.getElementById('targetSoC').textContent = targetSoC;
        document.getElementById('chargingProgress').textContent = Math.max(0, Math.min(100, progress));
        document.getElementById('chargingRate').textContent = session.charging_rate_kw.toFixed(1);
        document.getElementById('energyAdded').textContent = session.energy_added_kwh.toFixed(2);
        document.getElementById('chargingCost').textContent = '$' + session.cost.toFixed(2);
        document.getElementById('chargingLocation').textContent = session.location;
        
        // Update progress bar
        const progressFill = document.getElementById('progressFill');
        progressFill.style.width = Math.max(0, Math.min(100, progress)) + '%';
        
        // Update battery fill
        const batteryFill = document.getElementById('batteryFill');
        batteryFill.style.width = currentSoC + '%';
    }
    
    showNotChargingView() {
        // Update status indicator
        const indicator = document.getElementById('chargingStatusIndicator');
        indicator.textContent = 'Not Charging';
        indicator.classList.remove('charging');
        
        // Show/hide views
        document.getElementById('notChargingView').classList.remove('hidden');
        document.getElementById('chargingView').classList.add('hidden');
        
        // Update buttons
        document.getElementById('startChargingBtn').classList.remove('hidden');
        document.getElementById('stopChargingBtn').classList.add('hidden');
    }
    
    showStartModal() {
        document.getElementById('startChargingModal').classList.remove('hidden');
        // Set default target to current charge limit
        document.getElementById('targetSoCInput').value = this.chargeLimit;
    }
    
    hideStartModal() {
        document.getElementById('startChargingModal').classList.add('hidden');
    }
    
    async startCharging() {
        const targetSoC = parseInt(document.getElementById('targetSoCInput').value);
        
        if (targetSoC < 1 || targetSoC > 100) {
            this.showToast('Target SoC must be between 1 and 100', 'error');
            return;
        }
        
        try {
            const response = await this.apiClient.post('/api/charging/start', {
                target_soc: targetSoC
            });
            
            if (response.success) {
                this.showToast('Charging started successfully', 'success');
                this.hideStartModal();
                await this.updateChargingStatus();
            } else {
                this.showToast(response.error || 'Failed to start charging', 'error');
            }
        } catch (error) {
            console.error('Error starting charging:', error);
            this.showToast('Error starting charging', 'error');
        }
    }
    
    async stopCharging() {
        if (!confirm('Are you sure you want to stop charging?')) {
            return;
        }
        
        try {
            const response = await this.apiClient.post('/api/charging/stop');
            
            if (response.success) {
                this.showToast('Charging stopped', 'success');
                await this.updateChargingStatus();
                await this.loadHistory(); // Refresh history with new session
            } else {
                this.showToast(response.error || 'Failed to stop charging', 'error');
            }
        } catch (error) {
            console.error('Error stopping charging:', error);
            this.showToast('Error stopping charging', 'error');
        }
    }
    
    async saveChargeLimit() {
        const limit = parseInt(document.getElementById('limitSlider').value);
        
        try {
            const response = await this.apiClient.put('/api/charging/limit', {
                limit: limit
            });
            
            if (response.success) {
                this.chargeLimit = response.charge_limit;
                this.showToast('Charge limit saved', 'success');
            } else {
                this.showToast(response.error || 'Failed to save limit', 'error');
            }
        } catch (error) {
            console.error('Error saving charge limit:', error);
            this.showToast('Error saving charge limit', 'error');
        }
    }
    
    async loadHistory() {
        try {
            const response = await this.apiClient.get('/api/charging/history?limit=10');
            
            if (response.success) {
                this.displayHistory(response.sessions);
            }
        } catch (error) {
            console.error('Error loading history:', error);
            document.getElementById('historyList').innerHTML = 
                '<p class="empty-message">Error loading history</p>';
        }
    }
    
    displayHistory(sessions) {
        const historyList = document.getElementById('historyList');
        
        if (sessions.length === 0) {
            historyList.innerHTML = '<p class="empty-message">No charging history yet</p>';
            return;
        }
        
        historyList.innerHTML = sessions.map(session => {
            const startDate = new Date(session.start_time);
            const endDate = session.end_time ? new Date(session.end_time) : null;
            
            const duration = endDate ? 
                this.formatDuration((endDate - startDate) / 1000) : 'In progress';
            
            return `
                <div class="history-item">
                    <div class="history-item-header">
                        <span class="history-location">${session.location}</span>
                        <span class="history-date">${startDate.toLocaleDateString()} ${startDate.toLocaleTimeString()}</span>
                    </div>
                    <div class="history-item-details">
                        <div class="history-detail">
                            <span class="label">SoC:</span>
                            <span class="value">${Math.round(session.start_soc)}% → ${Math.round(session.current_soc)}%</span>
                        </div>
                        <div class="history-detail">
                            <span class="label">Energy:</span>
                            <span class="value">${session.energy_added_kwh.toFixed(2)} kWh</span>
                        </div>
                        <div class="history-detail">
                            <span class="label">Cost:</span>
                            <span class="value">$${session.cost.toFixed(2)}</span>
                        </div>
                        <div class="history-detail">
                            <span class="label">Duration:</span>
                            <span class="value">${duration}</span>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    formatDuration(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        }
        return `${minutes}m`;
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
    
    startStatusPolling() {
        // Poll every 2 seconds when charging, every 5 seconds when not
        this.updateInterval = setInterval(() => {
            this.updateChargingStatus();
            
            // Update battery level from vehicle status
            this.apiClient.get('/api/vehicle/status').then(response => {
                if (response.success) {
                    const batteryLevel = Math.round(response.data.battery_soc);
                    document.getElementById('batteryLevel').textContent = batteryLevel;
                    document.getElementById('modalCurrentSoC').textContent = batteryLevel;
                }
            });
        }, this.currentSession ? 2000 : 5000);
    }
    
    stopStatusPolling() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChargingManager();
});
