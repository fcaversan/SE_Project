# Research & Technology Decisions
## Home Screen & Vehicle Status Feature

**Date**: 2025-12-07  
**Feature**: 001-home-screen-vehicle-status

This document consolidates research findings and technology decisions made during Phase 0 planning.

---

## 1. Flask Application Structure for Simple Web Apps

### Decision
Use **Blueprint-less Flask structure** for this prototype with direct route definitions in `app.py`.

### Rationale
- Prototype scope doesn't warrant Flask Blueprints (adds unnecessary complexity)
- Simple route structure (`/`, `/api/vehicle/status`, etc.) can live in single file
- Follows Constitution Principle V (Web-Based Simplicity)

### Implementation Pattern
```python
# app.py structure
from flask import Flask, render_template, jsonify
from services.vehicle_data_service import VehicleDataService

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/api/vehicle/status')
def get_vehicle_status():
    # Implementation
    pass
```

### Alternatives Considered
- **Flask Blueprints**: Too complex for 4-5 routes
- **Flask-RESTX**: Adds framework overhead, contradicts simplicity principle

---

## 2. Mock Data Patterns in Python

### Decision
Use **class-based mock service** with `time.sleep()` for delays and configurable response scenarios.

### Rationale
- Simple, predictable simulation of async behavior
- Easy to configure different scenarios (normal, error, slow, offline)
- No external dependencies needed
- Aligns with Constitution Principle VI (Mock-First Integration)

### Implementation Pattern
```python
import time
import random
from models.vehicle_state import VehicleState

class VehicleDataMockService:
    def __init__(self, delay_range=(1, 3), failure_rate=0.0):
        self.delay_range = delay_range
        self.failure_rate = failure_rate
    
    def get_vehicle_status(self):
        # Simulate network delay
        time.sleep(random.uniform(*self.delay_range))
        
        # Simulate occasional failures
        if random.random() < self.failure_rate:
            raise ConnectionError("Mock: Vehicle unreachable")
        
        # Return mock data
        return VehicleState(
            state_of_charge=82,
            estimated_range=350,
            # ... other fields
        )
```

### Alternatives Considered
- **AsyncIO with async/await**: Overcomplicated for prototype, requires async Flask
- **Threading**: Unnecessary complexity, `time.sleep()` sufficient for demo

---

## 3. JSON File Persistence Best Practices

### Decision
Use **atomic writes with temp files** and Python's `fcntl` (Unix) or `msvcrt` (Windows) for file locking.

### Rationale
- Atomic writes prevent corruption if process crashes mid-write
- File locking prevents race conditions in concurrent access
- Simple pattern without database overhead

### Implementation Pattern
```python
import json
import os
import tempfile
import fcntl  # Unix-like systems
# import msvcrt  # Windows alternative

def save_json_atomic(data, filepath):
    """Atomically write data to JSON file"""
    # Write to temp file first
    fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(filepath))
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(data, f, indent=2)
        # Atomic rename
        os.replace(temp_path, filepath)
    except:
        os.unlink(temp_path)
        raise

def load_json_safe(filepath, default=None):
    """Safely load JSON with file locking"""
    if not os.path.exists(filepath):
        return default or {}
    
    with open(filepath, 'r') as f:
        fcntl.flock(f, fcntl.LOCK_SH)  # Shared lock for reading
        try:
            return json.load(f)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
```

### Alternatives Considered
- **No locking**: Risk of race conditions
- **Database (SQLite)**: Violates Constitution (no databases in prototype)

---

## 4. Frontend Data Binding Without Frameworks

### Decision
Use **direct DOM manipulation** with template literals and `document.querySelector()`.

### Rationale
- Simple, no build tools required
- Aligns with Constitution Principle V (vanilla JavaScript)
- Adequate performance for single-page home screen

### Implementation Pattern
```javascript
// Update battery display
function updateBatteryDisplay(vehicleData) {
    const socElement = document.querySelector('.battery-percentage');
    const rangeElement = document.querySelector('.estimated-range');
    
    socElement.textContent = `${vehicleData.state_of_charge}%`;
    rangeElement.textContent = `${vehicleData.estimated_range} km`;
    
    // Update battery visual
    const batteryFill = document.querySelector('.battery-fill');
    batteryFill.style.width = `${vehicleData.state_of_charge}%`;
}

// Pull-to-refresh implementation
let startY = 0;
const refreshThreshold = 80;

document.addEventListener('touchstart', e => {
    startY = e.touches[0].pageY;
});

document.addEventListener('touchmove', e => {
    const currentY = e.touches[0].pageY;
    const pullDistance = currentY - startY;
    
    if (pullDistance > refreshThreshold && window.scrollY === 0) {
        showRefreshIndicator();
    }
});

document.addEventListener('touchend', async e => {
    if (isPullRefreshTriggered()) {
        await refreshVehicleData();
    }
    hideRefreshIndicator();
});
```

### Alternatives Considered
- **React/Vue/Alpine.js**: Violates Constitution (no frameworks)
- **jQuery**: Unnecessary dependency for simple DOM manipulation

---

## 5. Range Calculation Algorithms for EVs

### Decision
Use **simplified linear model** with temperature adjustment factor.

### Rationale
- Adequate for prototype demonstration
- Documented as simplified (allows future refinement)
- Uses industry-standard factors (efficiency, temperature impact)

### Algorithm
```python
def calculate_estimated_range(soc, battery_capacity_kwh=75, 
                              efficiency_wh_per_km=150, 
                              ambient_temp_c=20):
    """
    Calculate estimated range based on current state.
    
    Args:
        soc: State of charge (0-100 %)
        battery_capacity_kwh: Total battery capacity in kWh
        efficiency_wh_per_km: Average efficiency in Wh/km
        ambient_temp_c: Current temperature in Celsius
    
    Returns:
        Estimated range in kilometers
    """
    # Available energy
    available_kwh = (soc / 100.0) * battery_capacity_kwh
    
    # Temperature adjustment (industry standard factors)
    if ambient_temp_c < 0:
        temp_factor = 0.7  # 30% reduction in cold
    elif ambient_temp_c < 10:
        temp_factor = 0.85  # 15% reduction in cool weather
    elif ambient_temp_c > 35:
        temp_factor = 0.9  # 10% reduction in heat (AC usage)
    else:
        temp_factor = 1.0  # Optimal range
    
    # Calculate range
    range_km = (available_kwh * 1000 / efficiency_wh_per_km) * temp_factor
    
    return round(range_km)
```

### Reference Data
- **Typical EV Battery**: 60-100 kWh capacity
- **Typical Efficiency**: 150-180 Wh/km (city driving)
- **Temperature Impact**: Based on Tes la/Nissan Leaf published data
  - Cold weather (<0°C): 20-40% range reduction
  - Hot weather (>35°C): 5-15% range reduction

### Alternatives Considered
- **Machine learning model**: Overkill for prototype
- **Physics-based model**: Too complex, requires detailed vehicle data

---

## 6. CSS Responsive Design Patterns

### Decision
Use **mobile-first CSS** with CSS Grid for main layout and Flexbox for components.

### Rationale
- Mobile-first ensures good experience on all screen sizes
- CSS Grid excellent for page-level layout
- Flexbox perfect for component-level arrangement
- No JavaScript media queries needed

### Implementation Pattern
```css
/* CSS Variables for theming */
:root {
    --color-primary: #007AFF;
    --color-success: #34C759;
    --color-warning: #FF9500;
    --color-danger: #FF3B30;
    --color-bg: #FFFFFF;
    --color-text: #000000;
    --spacing-unit: 8px;
}

/* Dark mode */
@media (prefers-color-scheme: dark) {
    :root {
        --color-bg: #000000;
        --color-text: #FFFFFF;
    }
}

/* Mobile-first layout */
.home-screen {
    display: grid;
    grid-template-rows: auto 1fr auto;
    gap: calc(var(--spacing-unit) * 2);
    padding: var(--spacing-unit);
}

/* Component: Battery status */
.battery-status {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-unit);
}

/* Tablet and up */
@media (min-width: 768px) {
    .home-screen {
        grid-template-columns: 1fr 1fr;
        padding: calc(var(--spacing-unit) * 3);
    }
}
```

### Browser Support
- **CSS Grid**: All modern browsers (Chrome 57+, Firefox 52+, Safari 10.1+, Edge 16+)
- **CSS Variables**: All modern browsers (Chrome 49+, Firefox 31+, Safari 9.1+, Edge 15+)
- **Flexbox**: Universal support in target browsers

### Alternatives Considered
- **CSS Frameworks (Bootstrap, Tailwind)**: Adds unnecessary complexity and bundle size
- **Float-based layout**: Outdated, harder to maintain
- **Table-based layout**: Inflexible, poor accessibility

---

## 7. Auto-Refresh Strategy

### Decision
Use **Page Visibility API** with `setInterval()` to pause polling when page hidden.

### Rationale
- Prevents unnecessary API calls when user switches tabs
- Conserves resources (important for mobile devices)
- Standard web platform API

### Implementation Pattern
```javascript
let refreshInterval = null;
const REFRESH_INTERVAL_MS = 60000; // 60 seconds

function startAutoRefresh() {
    refreshInterval = setInterval(async () => {
        if (document.visibilityState === 'visible') {
            await refreshVehicleData();
        }
    }, REFRESH_INTERVAL_MS);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
    }
}

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        // Page became visible - refresh immediately
        refreshVehicleData();
    }
});

// Start on page load
window.addEventListener('load', startAutoRefresh);
```

### Alternatives Considered
- **WebSockets**: Overcomplicated for prototype, requires persistent connection
- **Server-Sent Events (SSE)**: Unnecessary for 60-second polling
- **Always-on polling**: Wastes resources when page hidden

---

## 8. Error Handling Strategy

### Decision
Use **three-tier error handling**: Try-catch in service layer, error states in presenter, user-friendly messages in UI.

### Rationale
- Separates technical errors from user-facing messages
- Allows graceful degradation (show cached data on error)
- Aligns with Constitution Principle III (User-Centric Design)

### Implementation Pattern
```python
# Service layer - technical errors
class VehicleDataService:
    def get_vehicle_status(self):
        try:
            return self._fetch_from_api()
        except ConnectionError as e:
            raise VehicleUnavailableError("Vehicle offline") from e
        except TimeoutError as e:
            raise VehicleTimeoutError("Request timed out") from e

# Presenter layer - error states
class HomeScreenPresenter:
    def format_for_display(self, vehicle_state=None, error=None):
        if error:
            return {
                'status': 'error',
                'message': self._user_friendly_message(error),
                'cached_data': self._load_cached_data()
            }
        # ... normal formatting

# Frontend - user messages
const ERROR_MESSAGES = {
    'VEHICLE_OFFLINE': 'Unable to reach your vehicle. Showing last known status.',
    'NETWORK_ERROR': 'Connection problem. Please check your internet and try again.',
    'TIMEOUT': 'Request timed out. Pull down to retry.',
    'UNKNOWN': 'Something went wrong. Please try again later.'
};
```

---

## Summary of Key Decisions

| Area | Technology/Pattern | Rationale |
|------|-------------------|-----------|
| Backend Framework | Flask (simple routes, no Blueprints) | Simplicity for prototype |
| Mock Data | Class-based with `time.sleep()` delays | Predictable simulation |
| Persistence | Atomic writes + file locking | Prevents corruption |
| Frontend | Vanilla JS with direct DOM manipulation | No frameworks principle |
| Range Calculation | Linear model with temp adjustment | Adequate for demo |
| Layout | CSS Grid + Flexbox, mobile-first | Modern, responsive |
| Auto-Refresh | Page Visibility API + setInterval | Resource-efficient |
| Error Handling | Three-tier (service/presenter/UI) | Graceful degradation |

All decisions align with project constitution principles and support the prototype-first development approach.
