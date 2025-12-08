/**
 * Remote Controls JavaScript
 * 
 * Handles lock/unlock commands with optimistic UI updates, haptic feedback,
 * and error handling with retry logic.
 */

(function() {
    'use strict';

    // DOM Elements
    let lockButton;
    let unlockButton;
    let lockStatusText;
    let lockStatusIcon;
    let lockCommandFeedback;
    let toast;
    let toastMessage;

    // State
    let currentLockStatus = null;
    let commandInProgress = false;

    /**
     * Initialize the controls page
     */
    function init() {
        // Get DOM elements
        lockButton = document.getElementById('lockButton');
        unlockButton = document.getElementById('unlockButton');
        lockStatusText = document.getElementById('lockStatusText');
        lockStatusIcon = document.getElementById('lockStatusIcon');
        lockCommandFeedback = document.getElementById('lockCommandFeedback');
        toast = document.getElementById('toast');
        toastMessage = document.getElementById('toastMessage');

        // Attach event listeners
        lockButton.addEventListener('click', handleLock);
        unlockButton.addEventListener('click', handleUnlock);

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
