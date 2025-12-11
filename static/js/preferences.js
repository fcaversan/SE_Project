/**
 * Preferences Page Manager
 * Handles user preferences and settings
 */

class PreferencesManager {
    constructor() {
        this.currentUserId = 'default';
        this.preferences = null;
        this.init();
    }

    init() {
        this.setupTabs();
        this.setupForms();
        this.loadPreferences();
    }

    setupTabs() {
        const tabButtons = document.querySelectorAll('.tab-button');
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.switchTab(button.dataset.tab);
            });
        });
    }

    switchTab(tabName) {
        // Update buttons
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }

    setupForms() {
        // Profile form
        const profileForm = document.getElementById('profile-form');
        profileForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveProfile();
        });

        // Notifications form
        const notificationsForm = document.getElementById('notifications-form');
        notificationsForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveNotifications();
        });

        // Display form
        const displayForm = document.getElementById('display-form');
        displayForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveDisplay();
        });

        // Vehicle form
        const vehicleForm = document.getElementById('vehicle-form');
        vehicleForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveVehicle();
        });

        // Reset button
        const resetBtn = document.getElementById('reset-preferences-btn');
        resetBtn.addEventListener('click', () => {
            this.resetPreferences();
        });
    }

    async loadPreferences() {
        try {
            const response = await fetch(`/api/preferences/${this.currentUserId}`);
            const data = await response.json();

            if (data.success) {
                this.preferences = data.preferences;
                this.populateForms();
            } else {
                this.showToast('Failed to load preferences', 'error');
            }
        } catch (error) {
            console.error('Error loading preferences:', error);
            this.showToast('Error loading preferences', 'error');
        }
    }

    populateForms() {
        if (!this.preferences) return;

        // Profile
        document.getElementById('name').value = this.preferences.profile.name || '';
        document.getElementById('email').value = this.preferences.profile.email || '';
        document.getElementById('phone').value = this.preferences.profile.phone || '';

        // Notifications
        const notifications = this.preferences.notifications;
        document.getElementById('charging_complete').checked = notifications.charging_complete;
        document.getElementById('charging_interrupted').checked = notifications.charging_interrupted;
        document.getElementById('low_battery').checked = notifications.low_battery;
        document.getElementById('low_battery_threshold').value = notifications.low_battery_threshold;
        document.getElementById('software_updates').checked = notifications.software_updates;
        document.getElementById('service_reminders').checked = notifications.service_reminders;
        document.getElementById('trip_updates').checked = notifications.trip_updates;

        // Display
        const display = this.preferences.display;
        document.getElementById('distance_unit').value = display.distance_unit;
        document.getElementById('temperature_unit').value = display.temperature_unit;
        document.getElementById('energy_unit').value = display.energy_unit;
        document.getElementById('time_format').value = display.time_format;
        document.getElementById('theme').value = display.theme;
        document.getElementById('language').value = display.language;
        document.getElementById('show_range').checked = display.show_range;
        document.getElementById('show_charging_stations').checked = display.show_charging_stations;

        // Vehicle
        const vehicle = this.preferences.vehicle;
        document.getElementById('default_charging_limit').value = vehicle.default_charging_limit;
        document.getElementById('max_charging_current').value = vehicle.max_charging_current;
        document.getElementById('departure_time').value = vehicle.departure_time;
        document.getElementById('regenerative_braking').value = vehicle.regenerative_braking;
        document.getElementById('preconditioning_enabled').checked = vehicle.preconditioning_enabled;
        document.getElementById('seat_heating_auto').checked = vehicle.seat_heating_auto;
        document.getElementById('steering_wheel_heating_auto').checked = vehicle.steering_wheel_heating_auto;
        document.getElementById('climate_auto_on').checked = vehicle.climate_auto_on;
    }

    async saveProfile() {
        const profileData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value
        };

        try {
            const response = await fetch(`/api/preferences/${this.currentUserId}/profile`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(profileData)
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Profile saved successfully', 'success');
                await this.loadPreferences();
            } else {
                this.showToast(data.error || 'Failed to save profile', 'error');
            }
        } catch (error) {
            console.error('Error saving profile:', error);
            this.showToast('Error saving profile', 'error');
        }
    }

    async saveNotifications() {
        const notificationData = {
            charging_complete: document.getElementById('charging_complete').checked,
            charging_interrupted: document.getElementById('charging_interrupted').checked,
            low_battery: document.getElementById('low_battery').checked,
            low_battery_threshold: parseInt(document.getElementById('low_battery_threshold').value),
            software_updates: document.getElementById('software_updates').checked,
            service_reminders: document.getElementById('service_reminders').checked,
            trip_updates: document.getElementById('trip_updates').checked
        };

        try {
            const response = await fetch(`/api/preferences/${this.currentUserId}/notifications`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(notificationData)
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Notification settings saved', 'success');
                await this.loadPreferences();
            } else {
                this.showToast(data.error || 'Failed to save notifications', 'error');
            }
        } catch (error) {
            console.error('Error saving notifications:', error);
            this.showToast('Error saving notifications', 'error');
        }
    }

    async saveDisplay() {
        const displayData = {
            distance_unit: document.getElementById('distance_unit').value,
            temperature_unit: document.getElementById('temperature_unit').value,
            energy_unit: document.getElementById('energy_unit').value,
            time_format: document.getElementById('time_format').value,
            theme: document.getElementById('theme').value,
            language: document.getElementById('language').value,
            show_range: document.getElementById('show_range').checked,
            show_charging_stations: document.getElementById('show_charging_stations').checked
        };

        try {
            const response = await fetch(`/api/preferences/${this.currentUserId}/display`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(displayData)
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Display settings saved', 'success');
                await this.loadPreferences();
                this.applyTheme(displayData.theme);
            } else {
                this.showToast(data.error || 'Failed to save display settings', 'error');
            }
        } catch (error) {
            console.error('Error saving display settings:', error);
            this.showToast('Error saving display settings', 'error');
        }
    }

    async saveVehicle() {
        const vehicleData = {
            default_charging_limit: parseInt(document.getElementById('default_charging_limit').value),
            max_charging_current: parseInt(document.getElementById('max_charging_current').value),
            departure_time: document.getElementById('departure_time').value,
            regenerative_braking: document.getElementById('regenerative_braking').value,
            preconditioning_enabled: document.getElementById('preconditioning_enabled').checked,
            seat_heating_auto: document.getElementById('seat_heating_auto').checked,
            steering_wheel_heating_auto: document.getElementById('steering_wheel_heating_auto').checked,
            climate_auto_on: document.getElementById('climate_auto_on').checked
        };

        try {
            const response = await fetch(`/api/preferences/${this.currentUserId}/vehicle`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(vehicleData)
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Vehicle settings saved', 'success');
                await this.loadPreferences();
            } else {
                this.showToast(data.error || 'Failed to save vehicle settings', 'error');
            }
        } catch (error) {
            console.error('Error saving vehicle settings:', error);
            this.showToast('Error saving vehicle settings', 'error');
        }
    }

    async resetPreferences() {
        if (!confirm('Are you sure you want to reset all preferences to defaults? This cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch(`/api/preferences/${this.currentUserId}/reset`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('Preferences reset to defaults', 'success');
                await this.loadPreferences();
            } else {
                this.showToast(data.error || 'Failed to reset preferences', 'error');
            }
        } catch (error) {
            console.error('Error resetting preferences:', error);
            this.showToast('Error resetting preferences', 'error');
        }
    }

    applyTheme(theme) {
        if (theme === 'auto') {
            // Detect system theme
            const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            theme = darkModeMediaQuery.matches ? 'dark' : 'light';
        }
        document.documentElement.setAttribute('data-theme', theme);
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        const toastMessage = toast.querySelector('.toast-message');

        toastMessage.textContent = message;
        toast.className = `toast ${type}`;
        toast.classList.remove('hidden');

        setTimeout(() => {
            toast.classList.add('hidden');
        }, 3000);
    }
}

// Initialize preferences manager
const preferencesManager = new PreferencesManager();
