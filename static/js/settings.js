/**
 * Settings Page JavaScript
 * Handles user preference updates
 */

// DOM Elements
const settingsForm = document.getElementById('settings-form');
const saveStatus = document.getElementById('save-status');

/**
 * Initialize settings page
 */
async function initSettings() {
    await loadCurrentSettings();
    setupFormHandlers();
}

/**
 * Load current user settings
 */
async function loadCurrentSettings() {
    try {
        const response = await getUserProfile();
        
        if (response.success) {
            const profile = response.data;
            
            // Set unit system radio
            const unitRadio = document.querySelector(`input[name="unit_system"][value="${profile.unit_system}"]`);
            if (unitRadio) unitRadio.checked = true;
            
            // Set temperature unit radio
            const tempRadio = document.querySelector(`input[name="temp_unit"][value="${profile.temp_unit}"]`);
            if (tempRadio) tempRadio.checked = true;
        }
    } catch (error) {
        console.error('Failed to load settings:', error);
        showSaveStatus('Failed to load settings', 'error');
    }
}

/**
 * Setup form event handlers
 */
function setupFormHandlers() {
    settingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await saveSettings();
    });
}

/**
 * Save settings to server
 */
async function saveSettings() {
    const formData = new FormData(settingsForm);
    
    const profileData = {
        user_id: 'default',
        unit_system: formData.get('unit_system'),
        temp_unit: formData.get('temp_unit')
    };
    
    try {
        const response = await updateUserProfile(profileData);
        
        if (response.success) {
            showSaveStatus('Settings saved successfully!', 'success');
            
            // Redirect to home after 1.5 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showSaveStatus('Failed to save settings', 'error');
        }
    } catch (error) {
        console.error('Failed to save settings:', error);
        showSaveStatus('Failed to save settings', 'error');
    }
}

/**
 * Show save status message
 */
function showSaveStatus(message, type) {
    saveStatus.textContent = message;
    saveStatus.className = `save-status visible ${type}`;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        saveStatus.className = 'save-status hidden';
    }, 3000);
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSettings);
} else {
    initSettings();
}
