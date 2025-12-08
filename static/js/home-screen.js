/**
 * Home Screen JavaScript
 * Handles vehicle status display, pull-to-refresh, and auto-refresh
 */

// State management
let userProfile = null;
let autoRefreshTimer = null;
let lastRefreshTime = 0;
const MIN_REFRESH_INTERVAL = 3000; // 3 seconds minimum between refreshes
const AUTO_REFRESH_INTERVAL = 60000; // 60 seconds

// Pull-to-refresh state
let touchStartY = 0;
let touchCurrentY = 0;
let isPulling = false;

// DOM Elements
const errorBanner = document.getElementById('error-banner');
const refreshIndicator = document.getElementById('refresh-indicator');
const batteryPercentage = document.getElementById('battery-percentage');
const batteryRange = document.getElementById('battery-range');
const batteryLevel = document.getElementById('battery-level');
const batteryIcon = document.getElementById('battery-icon');
const lastUpdatedBattery = document.getElementById('last-updated-battery');
const lockStatus = document.getElementById('lock-status');
const lockIcon = document.getElementById('lock-icon');
const securityWarning = document.getElementById('security-warning');
const cabinTemp = document.getElementById('cabin-temp');
const climateStatus = document.getElementById('climate-status');

/**
 * Initialize home screen
 */
async function initHomeScreen() {
    // Load user profile
    await loadUserProfile();
    
    // Load initial vehicle data
    await updateVehicleDisplay();
    
    // Setup pull-to-refresh
    setupPullToRefresh();
    
    // Setup auto-refresh with Page Visibility API
    setupAutoRefresh();
}

/**
 * Load user profile and preferences
 */
async function loadUserProfile() {
    try {
        const response = await getUserProfile();
        if (response.success) {
            userProfile = response.data;
        }
    } catch (error) {
        console.error('Failed to load user profile:', error);
        // Use default profile if loading fails
        userProfile = {
            user_id: 'default',
            unit_system: 'metric',
            temp_unit: 'celsius'
        };
    }
}

/**
 * Update vehicle display with current data
 */
async function updateVehicleDisplay() {
    try {
        showLoadingIndicator();
        
        const response = await getVehicleStatus();
        
        if (response.success || response.data) {
            const data = response.data;
            
            // Update battery display (User Story 1)
            updateBatteryDisplay(data, response.warnings);
            
            // Update lock display (User Story 2)
            updateLockDisplay(data, response.warnings);
            
            // Update climate display (User Story 3)
            updateClimateDisplay(data);
            
            // Handle stale data indicator
            if (response.is_stale) {
                showStaleDataWarning();
            } else {
                hideStaleDataWarning();
            }
            
            // Clear error banner if data loaded successfully
            if (response.success) {
                hideErrorBanner();
            } else {
                showErrorBanner(response.error, 'warning');
            }
        }
    } catch (error) {
        console.error('Failed to update vehicle display:', error);
        showErrorBanner('Unable to reach vehicle. Showing cached data.');
    } finally {
        hideLoadingIndicator();
    }
}

/**
 * Update battery display (User Story 1)
 */
function updateBatteryDisplay(data, warnings = {}) {
    const soc = data.battery_soc;
    const range = data.estimated_range_km;
    
    // Format battery percentage
    batteryPercentage.textContent = `${Math.round(soc)}%`;
    
    // Format range based on user preferences
    const rangeText = formatRange(range);
    batteryRange.textContent = rangeText;
    
    // Update battery level visual
    batteryLevel.style.width = `${soc}%`;
    
    // Update battery colors based on level
    batteryIcon.parentElement.className = 'status-card battery-card';
    if (warnings.critical_battery) {
        batteryIcon.parentElement.classList.add('battery-critical');
        batteryIcon.style.setProperty('--battery-color', 'var(--color-danger)');
        showCriticalBatteryWarning();
    } else if (warnings.low_battery) {
        batteryIcon.parentElement.classList.add('battery-low');
        batteryIcon.style.setProperty('--battery-color', 'var(--color-warning)');
    } else {
        batteryIcon.parentElement.classList.add('battery-normal');
        batteryIcon.style.setProperty('--battery-color', 'var(--color-success)');
    }
    
    // Update last updated timestamp
    lastUpdatedBattery.textContent = formatTimestamp(data.last_updated);
}

/**
 * Update lock status display (User Story 2)
 */
function updateLockDisplay(data, warnings = {}) {
    const isLocked = data.lock_status === 'locked';
    
    lockStatus.textContent = isLocked ? 'Locked' : 'Unlocked';
    lockIcon.textContent = isLocked ? '🔒' : '🔓';
    
    const lockCard = lockIcon.closest('.status-card');
    lockCard.className = 'status-card security-card';
    
    if (isLocked) {
        lockCard.classList.add('lock-locked');
        lockIcon.style.setProperty('--lock-color', 'var(--color-success)');
        hideElement(securityWarning);
    } else {
        lockCard.classList.add('lock-unlocked');
        lockIcon.style.setProperty('--lock-color', 'var(--color-warning)');
        lockIcon.classList.add('unlocked');
        
        // Show warning if unlocked too long
        if (warnings.unlocked_too_long) {
            showElement(securityWarning);
        } else {
            hideElement(securityWarning);
        }
    }
}

/**
 * Update climate display (User Story 3)
 */
function updateClimateDisplay(data) {
    const temp = data.cabin_temp_celsius;
    const isClimateOn = data.climate_on;
    
    // Format temperature based on user preferences
    const tempText = formatTemperature(temp);
    cabinTemp.textContent = tempText;
    
    // Update climate status
    climateStatus.textContent = isClimateOn ? 'Climate On' : 'Climate Off';
    climateStatus.className = 'climate-status';
    
    if (isClimateOn) {
        climateStatus.classList.add('active');
        climateStatus.style.setProperty('--climate-color', 'var(--color-primary)');
    } else {
        climateStatus.style.setProperty('--climate-color', 'var(--color-text-secondary)');
    }
}

/**
 * Format range based on user preferences
 */
function formatRange(rangeKm) {
    if (!userProfile) return `${Math.round(rangeKm)} km`;
    
    if (userProfile.unit_system === 'imperial') {
        const rangeMi = rangeKm * 0.621371;
        return `${Math.round(rangeMi)} mi`;
    }
    return `${Math.round(rangeKm)} km`;
}

/**
 * Format temperature based on user preferences
 */
function formatTemperature(tempC) {
    if (!userProfile) return `${Math.round(tempC)}°C`;
    
    if (userProfile.temp_unit === 'fahrenheit') {
        const tempF = (tempC * 9/5) + 32;
        return `${Math.round(tempF)}°F`;
    }
    return `${Math.round(tempC)}°C`;
}

/**
 * Setup pull-to-refresh gesture (User Story 5)
 */
function setupPullToRefresh() {
    const homeScreen = document.querySelector('.home-screen');
    
    homeScreen.addEventListener('touchstart', (e) => {
        if (window.scrollY === 0) {
            touchStartY = e.touches[0].clientY;
            isPulling = true;
        }
    });
    
    homeScreen.addEventListener('touchmove', (e) => {
        if (!isPulling) return;
        
        touchCurrentY = e.touches[0].clientY;
        const pullDistance = touchCurrentY - touchStartY;
        
        if (pullDistance > 80 && window.scrollY === 0) {
            showElement(refreshIndicator);
        }
    });
    
    homeScreen.addEventListener('touchend', async () => {
        if (!isPulling) return;
        
        const pullDistance = touchCurrentY - touchStartY;
        isPulling = false;
        
        if (pullDistance > 80) {
            await handleManualRefresh();
        } else {
            hideElement(refreshIndicator);
        }
    });
}

/**
 * Handle manual refresh (User Story 5)
 */
const handleManualRefresh = debounce(async function() {
    const now = Date.now();
    
    // Enforce minimum refresh interval
    if (now - lastRefreshTime < MIN_REFRESH_INTERVAL) {
        console.log('Refresh too soon, debouncing...');
        hideElement(refreshIndicator);
        return;
    }
    
    lastRefreshTime = now;
    
    try {
        showElement(refreshIndicator);
        const response = await refreshVehicleData();
        
        if (response.success) {
            const data = response.data;
            updateBatteryDisplay(data, response.warnings);
            updateLockDisplay(data, response.warnings);
            updateClimateDisplay(data);
            hideErrorBanner();
        }
    } catch (error) {
        console.error('Refresh failed:', error);
        showErrorBanner('Failed to refresh data');
    } finally {
        setTimeout(() => hideElement(refreshIndicator), 500);
    }
}, MIN_REFRESH_INTERVAL);

/**
 * Setup auto-refresh with Page Visibility API (User Story 5)
 */
function setupAutoRefresh() {
    // Auto-refresh every 60 seconds when page is visible
    autoRefreshTimer = setInterval(() => {
        if (!document.hidden) {
            updateVehicleDisplay();
        }
    }, AUTO_REFRESH_INTERVAL);
    
    // Handle page visibility changes
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) {
            // Refresh when page becomes visible
            updateVehicleDisplay();
        }
    });
}

/**
 * Show/hide UI elements
 */
function showErrorBanner(message, type = 'error') {
    errorBanner.textContent = message;
    errorBanner.className = `error-banner visible ${type}`;
}

function hideErrorBanner() {
    errorBanner.className = 'error-banner hidden';
}

function showLoadingIndicator() {
    // Could show skeleton loader here
}

function hideLoadingIndicator() {
    // Hide skeleton loader
}

function showStaleDataWarning() {
    document.querySelectorAll('.status-card').forEach(card => {
        card.classList.add('stale');
    });
}

function hideStaleDataWarning() {
    document.querySelectorAll('.status-card').forEach(card => {
        card.classList.remove('stale');
    });
}

function showCriticalBatteryWarning() {
    showErrorBanner('Critical battery level! Charge immediately.', 'error');
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHomeScreen);
} else {
    initHomeScreen();
}
