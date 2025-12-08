/**
 * Remote Controls JavaScript
 * 
 * Handles lock/unlock commands with optimistic UI updates, haptic feedback,
 * and error handling with retry logic.
 */

(function() {
    'use strict';

    // DOM Elements - Lock/Unlock
    let lockButton;
    let unlockButton;
    let lockStatusText;
    let lockStatusIcon;
    let lockCommandFeedback;
    
    // DOM Elements - Climate
    let climateButton;
    let climateButtonText;
    let climateStatusText;
    let climateBatteryInfo;
    let climateWarning;
    let tempSlider;
    let tempValue;
    let presetButtons;
    let climateCommandFeedback;
    let heatButtons;
    let steeringHeatToggle;
    let frontDefrostToggle;
    let rearDefrostToggle;
    let frontDefrostTimer;
    let rearDefrostTimer;
    
    // DOM Elements - Common
    let toast;
    let toastMessage;

    // State
    let currentLockStatus = null;
    let climateActive = false;
    let currentTemperature = 21.0;
    let isPluggedIn = false;
    let commandInProgress = false;
    let seatHeatLevels = {
        front_left: 'off',
        front_right: 'off',
        rear: 'off'
    };
    let defrostTimers = {
        front: null,
        rear: null
    };
    let defrostTimeRemaining = {
        front: 0,
        rear: 0
    };

    /**
     * Initialize the controls page
     */
    function init() {
        // Get DOM elements - Lock/Unlock
        lockButton = document.getElementById('lockButton');
        unlockButton = document.getElementById('unlockButton');
        lockStatusText = document.getElementById('lockStatusText');
        lockStatusIcon = document.getElementById('lockStatusIcon');
        lockCommandFeedback = document.getElementById('lockCommandFeedback');
        
        // Get DOM elements - Climate
        climateButton = document.getElementById('climateButton');
        climateButtonText = document.getElementById('climateButtonText');
        climateStatusText = document.getElementById('climateStatusText');
        climateBatteryInfo = document.getElementById('climateBatteryInfo');
        climateWarning = document.getElementById('climateWarning');
        tempSlider = document.getElementById('tempSlider');
        tempValue = document.getElementById('tempValue');
        presetButtons = document.querySelectorAll('.preset-button');
        climateCommandFeedback = document.getElementById('climateCommandFeedback');
        heatButtons = document.querySelectorAll('.heat-button');
        steeringHeatToggle = document.getElementById('steeringHeatToggle');
        frontDefrostToggle = document.getElementById('frontDefrostToggle');
        rearDefrostToggle = document.getElementById('rearDefrostToggle');
        frontDefrostTimer = document.getElementById('frontDefrostTimer');
        rearDefrostTimer = document.getElementById('rearDefrostTimer');
        
        // Get DOM elements - Common
        toast = document.getElementById('toast');
        toastMessage = document.getElementById('toastMessage');

        // Attach event listeners - Lock/Unlock
        lockButton.addEventListener('click', handleLock);
        unlockButton.addEventListener('click', handleUnlock);
        
        // Attach event listeners - Climate
        climateButton.addEventListener('click', handleClimateToggle);
        tempSlider.addEventListener('input', handleTempSliderChange);
        tempSlider.addEventListener('change', handleTempSliderCommit);
        
        presetButtons.forEach(button => {
            button.addEventListener('click', () => {
                const temp = parseFloat(button.dataset.temp);
                setTemperature(temp);
            });
        });
        
        // Attach event listeners - Heated Seats
        heatButtons.forEach(button => {
            button.addEventListener('click', () => {
                const seat = button.dataset.seat;
                const level = button.dataset.level;
                handleSeatHeat(seat, level);
            });
        });
        
        // Attach event listeners - Steering & Defrost
        steeringHeatToggle.addEventListener('change', handleSteeringHeat);
        frontDefrostToggle.addEventListener('change', () => handleDefrost('front'));
        rearDefrostToggle.addEventListener('change', () => handleDefrost('rear'));

        // Load initial vehicle status
        loadVehicleStatus();

        console.log('Remote Controls initialized');
    }

    /**
     * Load current vehicle status
     */
    async function loadVehicleStatus() {
        try {
            const response = await fetch('/api/vehicle/status');
            const result = await response.json();

            if (result.success && result.data) {
                updateLockStatus(result.data.lock_status);
                updateClimateStatus(result.data);
            } else {
                showToast('Unable to load vehicle status', 'error');
            }
        } catch (error) {
            console.error('Error loading vehicle status:', error);
            showToast('Connection error', 'error');
        }
    }

    /**
     * Update lock status display
     */
    function updateLockStatus(status) {
        currentLockStatus = status;

        if (status === 'locked') {
            lockStatusText.textContent = 'Locked';
            lockStatusIcon.textContent = '🔒';
            lockButton.disabled = true;
            unlockButton.disabled = false;
        } else if (status === 'unlocked') {
            lockStatusText.textContent = 'Unlocked';
            lockStatusIcon.textContent = '🔓';
            lockButton.disabled = false;
            unlockButton.disabled = true;
        } else {
            lockStatusText.textContent = 'Unknown';
            lockStatusIcon.textContent = '❓';
            lockButton.disabled = false;
            unlockButton.disabled = false;
        }
    }

    /**
     * Update climate status display
     */
    function updateClimateStatus(vehicleData) {
        // Update plugged-in status
        isPluggedIn = vehicleData.is_plugged_in || false;
        
        // Update climate state
        const climate = vehicleData.climate_settings;
        if (climate && climate.is_active) {
            climateActive = true;
            currentTemperature = climate.target_temp_celsius;
            
            climateStatusText.textContent = `Active • ${currentTemperature}°C`;
            climateButtonText.textContent = 'Stop Climate';
            climateButton.classList.add('active');
            
            // Enable temperature controls
            tempSlider.disabled = false;
            presetButtons.forEach(btn => btn.disabled = false);
            
            // Update slider and display
            tempSlider.value = currentTemperature;
            tempValue.textContent = currentTemperature;
            updatePresetSelection(currentTemperature);
            
            // Show battery info
            const batteryPercent = vehicleData.battery_soc || 0;
            const drainEstimate = estimateBatteryDrain(currentTemperature);
            climateBatteryInfo.textContent = `Battery: ${batteryPercent}% • ~${drainEstimate}% drain/10min`;
            climateBatteryInfo.classList.remove('hidden');
            
            // Show warning if not plugged in
            if (!isPluggedIn) {
                climateWarning.classList.remove('hidden');
            } else {
                climateWarning.classList.add('hidden');
            }
        } else {
            climateActive = false;
            climateStatusText.textContent = 'Off';
            climateButtonText.textContent = 'Start Climate';
            climateButton.classList.remove('active');
            
            // Disable temperature controls when off
            tempSlider.disabled = true;
            presetButtons.forEach(btn => btn.disabled = true);
            
            climateBatteryInfo.classList.add('hidden');
            climateWarning.classList.add('hidden');
        }
        
        // Check battery level
        const batteryPercent = vehicleData.battery_soc || 0;
        if (batteryPercent < 10) {
            climateButton.disabled = true;
            showToast('Battery too low for climate control', 'error');
        } else {
            climateButton.disabled = false;
        }
        
        // Update advanced climate controls
        updateAdvancedClimateControls(vehicleData);
    }
    
    /**
     * Update advanced climate controls (seats, steering, defrost)
     */
    function updateAdvancedClimateControls(vehicleData) {
        const climate = vehicleData.climate_settings;
        if (!climate) return;
        
        // Update seat heat buttons
        seatHeatLevels.front_left = climate.front_left_seat_heat || 'off';
        seatHeatLevels.front_right = climate.front_right_seat_heat || 'off';
        seatHeatLevels.rear = climate.rear_seat_heat || 'off';
        
        heatButtons.forEach(button => {
            const seat = button.dataset.seat;
            const level = button.dataset.level;
            const currentLevel = seatHeatLevels[seat];
            
            if (level === currentLevel) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
        
        // Update steering heat toggle
        steeringHeatToggle.checked = climate.steering_wheel_heat || false;
        
        // Update defrost toggles
        frontDefrostToggle.checked = climate.front_defrost || false;
        rearDefrostToggle.checked = climate.rear_defrost || false;
        
        // Start/stop defrost timers
        if (climate.front_defrost && !defrostTimers.front) {
            startDefrostTimer('front');
        } else if (!climate.front_defrost && defrostTimers.front) {
            stopDefrostTimer('front');
        }
        
        if (climate.rear_defrost && !defrostTimers.rear) {
            startDefrostTimer('rear');
        } else if (!climate.rear_defrost && defrostTimers.rear) {
            stopDefrostTimer('rear');
        }
    }
    
    /**
     * Handle seat heat button click
     */
    async function handleSeatHeat(seat, level) {
        if (commandInProgress) return;
        
        try {
            const response = await fetch('/api/vehicle/seat-heat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ seat, level })
            });
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to set seat heat');
            }
            
            // Poll for command completion
            const finalCommand = await pollCommandStatus(result.command_id);
            
            if (finalCommand.status === 'completed') {
                // Success - reload vehicle status
                await loadVehicleStatus();
                triggerHapticFeedback('success');
            } else {
                throw new Error(finalCommand.error_message || 'Command failed');
            }
        } catch (error) {
            console.error('Seat heat error:', error);
            showToast(error.message || 'Failed to set seat heat', 'error');
            triggerHapticFeedback('error');
        }
    }
    
    /**
     * Handle steering heat toggle
     */
    async function handleSteeringHeat(event) {
        if (commandInProgress) return;
        
        const enabled = event.target.checked;
        
        try {
            const response = await fetch('/api/vehicle/steering-heat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled })
            });
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to control steering heat');
            }
            
            // Poll for command completion
            const finalCommand = await pollCommandStatus(result.command_id);
            
            if (finalCommand.status === 'completed') {
                // Success - reload vehicle status
                await loadVehicleStatus();
                triggerHapticFeedback('success');
            } else {
                throw new Error(finalCommand.error_message || 'Command failed');
            }
        } catch (error) {
            console.error('Steering heat error:', error);
            showToast(error.message || 'Failed to control steering heat', 'error');
            triggerHapticFeedback('error');
            // Revert toggle
            event.target.checked = !enabled;
        }
    }
    
    /**
     * Handle defrost toggle
     */
    async function handleDefrost(position) {
        if (commandInProgress) return;
        
        const toggle = position === 'front' ? frontDefrostToggle : rearDefrostToggle;
        const enabled = toggle.checked;
        
        try {
            const response = await fetch('/api/vehicle/defrost', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ position, enabled })
            });
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error || 'Failed to control defrost');
            }
            
            // Poll for command completion
            const finalCommand = await pollCommandStatus(result.command_id);
            
            if (finalCommand.status === 'completed') {
                // Success - reload vehicle status
                await loadVehicleStatus();
                
                if (enabled) {
                    startDefrostTimer(position);
                } else {
                    stopDefrostTimer(position);
                }
                
                triggerHapticFeedback('success');
            } else {
                throw new Error(finalCommand.error_message || 'Command failed');
            }
        } catch (error) {
            console.error('Defrost error:', error);
            showToast(error.message || 'Failed to control defrost', 'error');
            triggerHapticFeedback('error');
            // Revert toggle
            toggle.checked = !enabled;
        }
    }
    
    /**
     * Start defrost auto-shutoff timer (15 minutes)
     */
    function startDefrostTimer(position) {
        defrostTimeRemaining[position] = 15 * 60; // 15 minutes in seconds
        
        const timerDisplay = position === 'front' ? frontDefrostTimer : rearDefrostTimer;
        timerDisplay.classList.remove('hidden');
        
        defrostTimers[position] = setInterval(() => {
            defrostTimeRemaining[position]--;
            
            const minutes = Math.floor(defrostTimeRemaining[position] / 60);
            const seconds = defrostTimeRemaining[position] % 60;
            timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')} remaining`;
            
            if (defrostTimeRemaining[position] <= 0) {
                stopDefrostTimer(position);
                // Auto turn off defrost
                const toggle = position === 'front' ? frontDefrostToggle : rearDefrostToggle;
                toggle.checked = false;
                handleDefrost(position);
            }
        }, 1000);
    }
    
    /**
     * Stop defrost timer
     */
    function stopDefrostTimer(position) {
        if (defrostTimers[position]) {
            clearInterval(defrostTimers[position]);
            defrostTimers[position] = null;
        }
        
        defrostTimeRemaining[position] = 0;
        const timerDisplay = position === 'front' ? frontDefrostTimer : rearDefrostTimer;
        timerDisplay.classList.add('hidden');
    }

    /**
     * Handle climate toggle button click
     */
    async function handleClimateToggle() {
        if (commandInProgress) return;

        if (climateActive) {
            // Stop climate
            await sendClimateCommand('stop');
        } else {
            // Check if user confirmed unplugged warning
            if (!isPluggedIn) {
                const confirmed = confirm(
                    'Vehicle is not plugged in. Climate control will drain battery.\n\n' +
                    'Estimated drain: ~' + estimateBatteryDrain(currentTemperature) + '% per 10 minutes\n\n' +
                    'Continue?'
                );
                if (!confirmed) {
                    return;
                }
            }
            
            // Start climate
            await sendClimateCommand('start', currentTemperature);
        }
    }

    /**
     * Handle temperature slider input (live update)
     */
    function handleTempSliderChange(e) {
        const temp = parseFloat(e.target.value);
        currentTemperature = temp;
        tempValue.textContent = temp;
        updatePresetSelection(temp);
    }

    /**
     * Handle temperature slider commit (user released slider)
     */
    async function handleTempSliderCommit(e) {
        const temp = parseFloat(e.target.value);
        
        // If climate is active, send update command
        if (climateActive) {
            await updateClimateTemperature(temp);
        }
    }

    /**
     * Set temperature (from preset buttons)
     */
    async function setTemperature(temp) {
        currentTemperature = temp;
        tempSlider.value = temp;
        tempValue.textContent = temp;
        updatePresetSelection(temp);
        
        // If climate is active, send update command
        if (climateActive) {
            await updateClimateTemperature(temp);
        }
    }

    /**
     * Update preset button selection state
     */
    function updatePresetSelection(temp) {
        presetButtons.forEach(btn => {
            const presetTemp = parseFloat(btn.dataset.temp);
            if (Math.abs(presetTemp - temp) < 0.1) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    /**
     * Estimate battery drain per 10 minutes
     */
    function estimateBatteryDrain(temp) {
        // Simple estimation: 1-3% based on temperature differential from 21°C
        const diff = Math.abs(temp - 21);
        const baseDrain = 1.0;
        const extraDrain = diff * 0.15;
        return Math.min(3.0, baseDrain + extraDrain).toFixed(1);
    }

    /**
     * Send climate command (start/stop)
     */
    async function sendClimateCommand(action, temperature = null) {
        commandInProgress = true;
        climateCommandFeedback.classList.remove('hidden');
        climateButton.disabled = true;

        // Build request body
        const body = { action };
        if (action === 'start' && temperature !== null) {
            body.temperature = temperature;
        }

        try {
            const response = await fetch('/api/vehicle/climate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Command failed');
            }

            // Poll for command completion
            const finalCommand = await pollCommandStatus(result.command_id);

            if (finalCommand.status === 'completed') {
                // Success - reload vehicle status
                await loadVehicleStatus();
                
                const message = action === 'start' 
                    ? 'Climate control started' 
                    : 'Climate control stopped';
                showToast(message, 'success');
                triggerHapticFeedback('success');
            } else {
                throw new Error(finalCommand.error_message || 'Command failed');
            }
        } catch (error) {
            console.error('Climate command error:', error);
            showToast(error.message || 'Failed to control climate', 'error');
            triggerHapticFeedback('error');
        } finally {
            commandInProgress = false;
            climateCommandFeedback.classList.add('hidden');
            climateButton.disabled = false;
        }
    }

    /**
     * Update climate temperature (while running)
     */
    async function updateClimateTemperature(temperature) {
        try {
            const response = await fetch('/api/vehicle/climate', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ temperature })
            });

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to update temperature');
            }

            // Poll for command completion
            const finalCommand = await pollCommandStatus(result.command_id);

            if (finalCommand.status === 'completed') {
                // Success - reload vehicle status
                await loadVehicleStatus();
                triggerHapticFeedback('success');
            } else {
                throw new Error(finalCommand.error_message || 'Command failed');
            }
        } catch (error) {
            console.error('Temperature update error:', error);
            showToast(error.message || 'Failed to update temperature', 'error');
            triggerHapticFeedback('error');
        }
    }

    /**
     * Handle lock button click
     */
    async function handleLock() {
        if (commandInProgress) return;

        await sendCommand('lock', 'locked', '🔒', 'Vehicle locked');
    }

    /**
     * Handle unlock button click
     */
    async function handleUnlock() {
        if (commandInProgress) return;

        await sendCommand('unlock', 'unlocked', '🔓', 'Vehicle unlocked');
    }

    /**
     * Send command to vehicle
     */
    async function sendCommand(commandType, targetStatus, targetIcon, successMessage) {
        commandInProgress = true;

        // Disable both buttons
        lockButton.disabled = true;
        unlockButton.disabled = true;

        // Show loading state
        const activeButton = commandType === 'lock' ? lockButton : unlockButton;
        activeButton.classList.add('loading');
        lockCommandFeedback.classList.remove('hidden');

        // Optimistic UI update
        const previousStatus = currentLockStatus;
        const previousIcon = lockStatusIcon.textContent;
        lockStatusText.textContent = commandType === 'lock' ? 'Locking...' : 'Unlocking...';
        lockStatusIcon.textContent = '⏳';

        try {
            // Send command
            const response = await fetch(`/api/vehicle/${commandType}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(result.error || 'Command failed');
            }

            const commandId = result.command_id;

            // Poll for command completion
            const finalStatus = await pollCommandStatus(commandId);

            if (finalStatus === 'success') {
                // Update to final state
                updateLockStatus(targetStatus);
                
                // Show success state
                activeButton.classList.remove('loading');
                activeButton.classList.add('success');
                
                // Trigger haptic feedback
                triggerHapticFeedback('success');
                
                // Show success toast
                showToast(successMessage, 'success');

                // Reset button state after animation
                setTimeout(() => {
                    activeButton.classList.remove('success');
                }, 500);
            } else {
                throw new Error('Command failed or timed out');
            }
        } catch (error) {
            console.error('Command error:', error);

            // Rollback optimistic update
            lockStatusText.textContent = previousStatus === 'locked' ? 'Locked' : 'Unlocked';
            lockStatusIcon.textContent = previousIcon;
            currentLockStatus = previousStatus;

            // Show error state
            activeButton.classList.remove('loading');
            activeButton.classList.add('error');
            
            // Trigger error haptic feedback
            triggerHapticFeedback('error');
            
            // Show error toast with retry option
            showToast(error.message || 'Command failed', 'error');

            // Reset button state after animation
            setTimeout(() => {
                activeButton.classList.remove('error');
                updateLockStatus(previousStatus);
            }, 500);
        } finally {
            lockCommandFeedback.classList.add('hidden');
            commandInProgress = false;
        }
    }

    /**
     * Poll command status until completion
     */
    async function pollCommandStatus(commandId, maxAttempts = 10, interval = 500) {
        for (let i = 0; i < maxAttempts; i++) {
            await sleep(interval);

            try {
                const response = await fetch(`/api/vehicle/commands/${commandId}`);
                const result = await response.json();

                if (result.success && result.data) {
                    const status = result.data.status;

                    if (status === 'success') {
                        return 'success';
                    } else if (status === 'failed' || status === 'timeout') {
                        return status;
                    }
                    // If pending, continue polling
                }
            } catch (error) {
                console.error('Error polling command status:', error);
            }
        }

        return 'timeout';
    }

    /**
     * Trigger haptic feedback (vibration)
     */
    function triggerHapticFeedback(type) {
        if (!navigator.vibrate) {
            return; // Vibration API not supported
        }

        if (type === 'success') {
            // Single 200ms vibration for success
            navigator.vibrate(200);
        } else if (type === 'error') {
            // Three short vibrations for error (50ms-50ms-50ms)
            navigator.vibrate([50, 50, 50, 50, 50]);
        }
    }

    /**
     * Show toast notification
     */
    function showToast(message, type = 'info') {
        toastMessage.textContent = message;
        toast.className = 'toast';
        
        if (type === 'success' || type === 'error') {
            toast.classList.add(type);
        }

        toast.classList.remove('hidden');

        // Hide after 3 seconds
        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }

    /**
     * Sleep utility
     */
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
