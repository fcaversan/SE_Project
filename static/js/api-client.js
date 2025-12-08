/**
 * API Client for Vehicle Connect
 * Handles HTTP requests with error handling
 */

const API_BASE = '/api';

/**
 * Fetch wrapper with error handling
 * @param {string} url - API endpoint URL
 * @param {Object} options - Fetch options
 * @returns {Promise<Object>} Response data
 */
async function fetchAPI(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Get vehicle status
 * @returns {Promise<Object>} Vehicle status data
 */
async function getVehicleStatus() {
    return fetchAPI(`${API_BASE}/vehicle/status`);
}

/**
 * Refresh vehicle data
 * @returns {Promise<Object>} Refreshed vehicle data
 */
async function refreshVehicleData() {
    return fetchAPI(`${API_BASE}/vehicle/refresh`, {
        method: 'POST',
    });
}

/**
 * Get user profile
 * @returns {Promise<Object>} User profile data
 */
async function getUserProfile() {
    return fetchAPI(`${API_BASE}/user/profile`);
}

/**
 * Update user profile
 * @param {Object} profileData - Profile data to update
 * @returns {Promise<Object>} Updated profile data
 */
async function updateUserProfile(profileData) {
    return fetchAPI(`${API_BASE}/user/profile`, {
        method: 'PUT',
        body: JSON.stringify(profileData),
    });
}
