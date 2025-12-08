/**
 * Utility functions for Vehicle Connect
 */

/**
 * Debounce function to limit rapid calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format timestamp as relative time
 * @param {string} isoTimestamp - ISO timestamp string
 * @returns {string} Relative time string (e.g., "2m ago")
 */
function formatTimestamp(isoTimestamp) {
    const date = new Date(isoTimestamp);
    const now = new Date();
    const diffSeconds = Math.floor((now - date) / 1000);
    
    if (diffSeconds < 60) {
        return `${diffSeconds}s ago`;
    } else if (diffSeconds < 3600) {
        const minutes = Math.floor(diffSeconds / 60);
        return `${minutes}m ago`;
    } else {
        const hours = Math.floor(diffSeconds / 3600);
        return `${hours}h ago`;
    }
}

/**
 * Show element with fade-in animation
 * @param {HTMLElement} element - Element to show
 */
function showElement(element) {
    if (element) {
        element.classList.remove('hidden');
        element.classList.add('visible');
    }
}

/**
 * Hide element with fade-out animation
 * @param {HTMLElement} element - Element to hide
 */
function hideElement(element) {
    if (element) {
        element.classList.remove('visible');
        element.classList.add('hidden');
    }
}

/**
 * Toggle element visibility
 * @param {HTMLElement} element - Element to toggle
 */
function toggleElement(element) {
    if (element) {
        if (element.classList.contains('hidden')) {
            showElement(element);
        } else {
            hideElement(element);
        }
    }
}

/**
 * Set text content safely
 * @param {string} selector - CSS selector or element ID
 * @param {string} text - Text to set
 */
function setText(selector, text) {
    const element = document.getElementById(selector) || document.querySelector(selector);
    if (element) {
        element.textContent = text;
    }
}

/**
 * Check if data is stale (older than threshold)
 * @param {string} timestamp - ISO timestamp string
 * @param {number} thresholdSeconds - Threshold in seconds
 * @returns {boolean} True if stale
 */
function isStale(timestamp, thresholdSeconds = 60) {
    const date = new Date(timestamp);
    const now = new Date();
    const ageSeconds = (now - date) / 1000;
    return ageSeconds > thresholdSeconds;
}
