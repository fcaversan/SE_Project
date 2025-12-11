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
        this.editingSchedule = null;
        
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
        
        // Charge limit preset buttons
        document.querySelectorAll('.limit-preset').forEach(preset => {
            preset.addEventListener('click', () => {
                const value = preset.getAttribute('data-value');
                limitSlider.value = value;
                document.getElementById('limitValue').textContent = value;
            });
        });
        
        // Save limit button
        document.getElementById('saveLimitBtn').addEventListener('click', () => {
            console.log('Save Limit button clicked');
            this.saveChargeLimit();
        });
        
        // Refresh history
        document.getElementById('refreshHistoryBtn').addEventListener('click', () => {
            this.loadHistory();
        });
        
        // Schedule management
        document.getElementById('addScheduleBtn').addEventListener('click', () => {
            this.showScheduleModal();
        });
        
        document.getElementById('closeScheduleModalBtn').addEventListener('click', () => {
            this.hideScheduleModal();
        });
        
        document.getElementById('cancelScheduleBtn').addEventListener('click', () => {
            this.hideScheduleModal();
        });
        
        document.getElementById('saveScheduleBtn').addEventListener('click', () => {
            this.saveSchedule();
        });
        
        // Time mode radio buttons
        document.querySelectorAll('input[name="timeMode"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.handleTimeModeChange(e.target.value);
            });
        });
    }
    
    async loadInitialData() {
        try {
            // Load vehicle status for battery level
            const vehicleStatus = await this.apiClient.get('/vehicle/status');
            if (vehicleStatus.success) {
                const batteryLevel = Math.round(vehicleStatus.data.battery_soc);
                document.getElementById('batteryLevel').textContent = batteryLevel;
                document.getElementById('modalCurrentSoC').textContent = batteryLevel;
            }
            
            // Load charging status
            await this.updateChargingStatus();
            
            // Load charge limit
            const limitResponse = await this.apiClient.get('/charging/limit');
            if (limitResponse.success) {
                this.chargeLimit = limitResponse.charge_limit;
                document.getElementById('limitValue').textContent = this.chargeLimit;
                document.getElementById('limitSlider').value = this.chargeLimit;
            }
            
            // Load charging history
            await this.loadHistory();
            
            // Load charging schedules
            await this.loadSchedules();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showToast('Error loading data', 'error');
        }
    }
    
    async updateChargingStatus() {
        try {
            const response = await this.apiClient.get('/charging/status');
            
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
            const response = await this.apiClient.post('/charging/start', {
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
            const response = await this.apiClient.post('/charging/stop');
            
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
        
        console.log('saveChargeLimit called with limit:', limit);
        
        try {
            const response = await this.apiClient.put('/charging/limit', {
                limit: limit
            });
            
            console.log('Limit save response:', response);
            
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
            const response = await this.apiClient.get('/charging/history?limit=10');
            
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
    
    // Schedule Management Methods
    
    async loadSchedules() {
        try {
            const response = await this.apiClient.get('/charging/schedules');
            
            if (response.success) {
                this.displaySchedules(response.schedules);
            }
        } catch (error) {
            console.error('Error loading schedules:', error);
            document.getElementById('schedulesList').innerHTML = 
                '<p class="empty-message">Error loading schedules</p>';
        }
    }
    
    displaySchedules(schedules) {
        const schedulesList = document.getElementById('schedulesList');
        
        if (schedules.length === 0) {
            schedulesList.innerHTML = '<p class="empty-message">No schedules yet. Create one to automate charging!</p>';
            return;
        }
        
        schedulesList.innerHTML = schedules.map(schedule => {
            const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            const days = schedule.days_of_week.sort((a, b) => a - b).map(d => dayNames[d]);
            
            const timeInfo = schedule.start_time ? 
                `Start at ${schedule.start_time}` : 
                `Ready by ${schedule.ready_by_time}`;
            
            const statusClass = schedule.enabled ? 'enabled' : 'disabled';
            const statusText = schedule.enabled ? 'Enabled' : 'Disabled';
            
            return `
                <div class="schedule-item ${schedule.enabled ? '' : 'disabled'}">
                    <div class="schedule-header">
                        <span class="schedule-name">${schedule.name}</span>
                        <span class="schedule-status ${statusClass}">${statusText}</span>
                    </div>
                    <div class="schedule-details">
                        <div class="schedule-detail">
                            <span class="label">Days:</span>
                            <div class="schedule-days">
                                ${days.map(day => `<span class="day-badge">${day}</span>`).join('')}
                            </div>
                        </div>
                        <div class="schedule-detail">
                            <span class="label">Time:</span>
                            <span class="value">${timeInfo}</span>
                        </div>
                        <div class="schedule-detail">
                            <span class="label">Target:</span>
                            <span class="value">${schedule.target_soc}%</span>
                        </div>
                    </div>
                    <div class="schedule-actions">
                        <button class="btn-icon" onclick="chargingManager.editSchedule('${schedule.schedule_id}')" title="Edit">
                            ✏️
                        </button>
                        <button class="btn-icon" onclick="chargingManager.toggleSchedule('${schedule.schedule_id}')" title="${schedule.enabled ? 'Disable' : 'Enable'}">
                            ${schedule.enabled ? '⏸️' : '▶️'}
                        </button>
                        <button class="btn-icon delete" onclick="chargingManager.deleteSchedule('${schedule.schedule_id}')" title="Delete">
                            🗑️
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    showScheduleModal(schedule = null) {
        this.editingSchedule = schedule;
        
        // Update modal title
        const modalTitle = document.getElementById('scheduleModalTitle');
        modalTitle.textContent = schedule ? 'Edit Schedule' : 'Add Schedule';
        
        if (schedule) {
            // Populate form with existing schedule data
            document.getElementById('scheduleNameInput').value = schedule.name;
            document.getElementById('targetSoCScheduleInput').value = schedule.target_soc;
            document.getElementById('enabledInput').checked = schedule.enabled;
            
            // Set days of week
            document.querySelectorAll('.day-checkbox input').forEach(checkbox => {
                checkbox.checked = schedule.days_of_week.includes(parseInt(checkbox.value));
            });
            
            // Set time mode and time
            if (schedule.start_time) {
                document.querySelector('input[name="timeMode"][value="start_time"]').checked = true;
                document.getElementById('startTimeInput').value = schedule.start_time;
                this.handleTimeModeChange('start_time');
            } else {
                document.querySelector('input[name="timeMode"][value="ready_by"]').checked = true;
                document.getElementById('readyByInput').value = schedule.ready_by_time;
                this.handleTimeModeChange('ready_by');
            }
        } else {
            // Reset form for new schedule
            document.getElementById('scheduleNameInput').value = '';
            document.getElementById('targetSoCScheduleInput').value = 80;
            document.getElementById('enabledInput').checked = true;
            document.getElementById('startTimeInput').value = '22:00';
            document.getElementById('readyByInput').value = '07:00';
            document.querySelector('input[name="timeMode"][value="start_time"]').checked = true;
            this.handleTimeModeChange('start_time');
            
            // Uncheck all days
            document.querySelectorAll('.day-checkbox input').forEach(checkbox => {
                checkbox.checked = false;
            });
        }
        
        document.getElementById('scheduleModal').classList.remove('hidden');
    }
    
    hideScheduleModal() {
        document.getElementById('scheduleModal').classList.add('hidden');
        this.editingSchedule = null;
    }
    
    handleTimeModeChange(mode) {
        const startTimeGroup = document.getElementById('startTimeGroup');
        const readyByGroup = document.getElementById('readyByGroup');
        
        if (mode === 'start_time') {
            startTimeGroup.classList.remove('hidden');
            readyByGroup.classList.add('hidden');
        } else {
            startTimeGroup.classList.add('hidden');
            readyByGroup.classList.remove('hidden');
        }
    }
    
    async saveSchedule() {
        // Collect form data
        const name = document.getElementById('scheduleNameInput').value.trim();
        const targetSoC = parseInt(document.getElementById('targetSoCScheduleInput').value);
        const enabled = document.getElementById('enabledInput').checked;
        
        // Get selected days
        const days = [];
        document.querySelectorAll('.day-checkbox input:checked').forEach(checkbox => {
            days.push(parseInt(checkbox.value));
        });
        
        // Get time mode and time
        const timeMode = document.querySelector('input[name="timeMode"]:checked').value;
        const startTime = document.getElementById('startTimeInput').value;
        const readyByTime = document.getElementById('readyByInput').value;
        
        // Validate
        if (!name) {
            this.showToast('Please enter a schedule name', 'error');
            return;
        }
        
        if (days.length === 0) {
            this.showToast('Please select at least one day', 'error');
            return;
        }
        
        if (targetSoC < 1 || targetSoC > 100) {
            this.showToast('Target SoC must be between 1 and 100', 'error');
            return;
        }
        
        // Build schedule data
        const scheduleData = {
            name: name,
            days_of_week: days,
            target_soc: targetSoC,
            enabled: enabled
        };
        
        if (timeMode === 'start_time') {
            scheduleData.start_time = startTime;
        } else {
            scheduleData.ready_by_time = readyByTime;
        }
        
        try {
            let response;
            if (this.editingSchedule) {
                // Update existing schedule
                response = await this.apiClient.put(
                    `/charging/schedules/${this.editingSchedule.schedule_id}`,
                    scheduleData
                );
            } else {
                // Create new schedule
                response = await this.apiClient.post('/charging/schedules', scheduleData);
            }
            
            if (response.success) {
                this.showToast(
                    this.editingSchedule ? 'Schedule updated' : 'Schedule created',
                    'success'
                );
                this.hideScheduleModal();
                await this.loadSchedules();
            } else {
                this.showToast(response.error || 'Failed to save schedule', 'error');
            }
        } catch (error) {
            console.error('Error saving schedule:', error);
            this.showToast('Error saving schedule', 'error');
        }
    }
    
    async editSchedule(scheduleId) {
        try {
            const response = await this.apiClient.get('/charging/schedules');
            
            if (response.success && response.schedules) {
                const schedule = response.schedules.find(s => s.schedule_id === scheduleId);
                if (schedule) {
                    this.showScheduleModal(schedule);
                } else {
                    console.error('Schedule not found:', scheduleId);
                    this.showToast('Schedule not found', 'error');
                }
            } else {
                console.error('Failed to fetch schedules:', response);
                this.showToast(response.error || 'Failed to load schedules', 'error');
            }
        } catch (error) {
            console.error('Error loading schedule:', error);
            this.showToast('Error loading schedule', 'error');
        }
    }
    
    async deleteSchedule(scheduleId) {
        if (!confirm('Are you sure you want to delete this schedule?')) {
            return;
        }
        
        try {
            const response = await this.apiClient.delete(`/charging/schedules/${scheduleId}`);
            
            if (response.success) {
                this.showToast('Schedule deleted', 'success');
                await this.loadSchedules();
            } else {
                this.showToast(response.error || 'Failed to delete schedule', 'error');
            }
        } catch (error) {
            console.error('Error deleting schedule:', error);
            this.showToast('Error deleting schedule', 'error');
        }
    }
    
    async toggleSchedule(scheduleId) {
        try {
            // Load current schedule
            const response = await this.apiClient.get('/charging/schedules');
            
            if (response.success) {
                const schedule = response.schedules.find(s => s.schedule_id === scheduleId);
                if (schedule) {
                    // Toggle enabled status
                    const updateData = {
                        name: schedule.name,
                        days_of_week: schedule.days_of_week,
                        target_soc: schedule.target_soc,
                        enabled: !schedule.enabled
                    };
                    
                    if (schedule.start_time) {
                        updateData.start_time = schedule.start_time;
                    } else {
                        updateData.ready_by_time = schedule.ready_by_time;
                    }
                    
                    const updateResponse = await this.apiClient.put(
                        `/charging/schedules/${scheduleId}`,
                        updateData
                    );
                    
                    if (updateResponse.success) {
                        this.showToast(
                            schedule.enabled ? 'Schedule disabled' : 'Schedule enabled',
                            'success'
                        );
                        await this.loadSchedules();
                    } else {
                        this.showToast(updateResponse.error || 'Failed to update schedule', 'error');
                    }
                }
            }
        } catch (error) {
            console.error('Error toggling schedule:', error);
            this.showToast('Error updating schedule', 'error');
        }
    }
    
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toastMessage');
        
        toastMessage.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.remove('hidden'); // Show the toast
        
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }
    
    startStatusPolling() {
        // Poll every 2 seconds when charging, every 5 seconds when not
        this.updateInterval = setInterval(() => {
            this.updateChargingStatus();
            
            // Update battery level from vehicle status
            this.apiClient.get('/vehicle/status').then(response => {
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
let chargingManager;
document.addEventListener('DOMContentLoaded', () => {
    chargingManager = new ChargingManager();
});
