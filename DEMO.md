# Vehicle Connect - Demo Script

## Feature Demonstration Guide

This script demonstrates all 5 user stories implemented in the Home Screen & Vehicle Status feature.

### Prerequisites

```powershell
# Ensure Flask server is running
cd c:\Projects\SE_Project
.\.venv\Scripts\python.exe app.py
```

Navigate to: `http://127.0.0.1:5000`

---

## User Story 1: Battery Status Display (P1 - MVP)

**Goal**: View battery percentage, range estimate, and visual indicators

**Demo Steps**:
1. Open home screen - observe battery section
2. Verify display shows:
   - Battery percentage (e.g., "82%")
   - Battery progress bar (green for normal)
   - Estimated range (e.g., "350 km")
   - Last updated timestamp

**Expected Behavior**:
- Battery icon fills proportionally to SoC
- Green color for normal (≥20%)
- Amber color for low (5-20%)
- Red color for critical (<5%)

**Test Scenarios**:
```powershell
# Change scenario to low battery
$env:MOCK_SCENARIO = "low_battery"
# Restart Flask app - observe amber warning

# Change to critical battery
$env:MOCK_SCENARIO = "critical_battery"
# Restart Flask app - observe red critical warning banner
```

---

## User Story 2: Security Status Monitor (P1)

**Goal**: Display lock status with security warnings

**Demo Steps**:
1. Observe security card on home screen
2. Default scenario shows: 🔒 "Locked" (green)
3. Change to unlocked scenario:

```powershell
$env:MOCK_SCENARIO = "unlocked"
# Restart Flask - observe 🔓 "Unlocked"
```

4. Change to prolonged unlock:

```powershell
$env:MOCK_SCENARIO = "unlocked_too_long"
# Restart Flask - observe amber warning: "Unlocked for over 10 minutes"
```

**Expected Behavior**:
- Locked: Green indicator with lock icon
- Unlocked: Amber indicator with unlock icon
- Unlocked >10 min: Amber warning banner appears

---

## User Story 3: Climate Control Status (P2)

**Goal**: Display cabin temperature and HVAC status

**Demo Steps**:
1. Default scenario shows: "22°C" and "Climate Off"
2. Change to climate active:

```powershell
$env:MOCK_SCENARIO = "climate_active"
# Restart Flask - observe "Climate On" with animated indicator
```

**Expected Behavior**:
- Temperature displays in user's preferred unit (°C or °F)
- "Climate On" shows pulsing animation
- "Climate Off" shows static text

**Test Unit Conversion**:
1. Navigate to Settings page (`/settings`)
2. Change temperature unit to Fahrenheit
3. Save settings
4. Return to home - observe "72°F" instead of "22°C"

---

## User Story 4: Vehicle Visualization (P3)

**Goal**: Display graphical vehicle representation

**Demo Steps**:
1. Home screen displays SVG vehicle image at top
2. Resize browser window - observe responsive scaling
3. Image maintains aspect ratio on mobile/tablet/desktop

**Expected Behavior**:
- Vehicle SVG loads and displays
- Scales responsively without obscuring data
- Gracefully handles missing image (hides if not found)

---

## User Story 5: Pull-to-Refresh & Auto-Refresh (P2)

**Goal**: Manual and automatic data refresh

**Demo Steps - Auto-Refresh**:
1. Open browser DevTools (F12) → Network tab
2. Wait 60 seconds
3. Observe automatic API call to `/api/vehicle/status`
4. Switch to different browser tab for >60s
5. Return to Vehicle Connect tab
6. Observe immediate refresh (Page Visibility API)

**Demo Steps - Pull-to-Refresh**:
1. On mobile/touch device: Pull down on home screen
2. Observe loading spinner: "Refreshing..."
3. Data updates with current timestamp
4. Try rapid pull-to-refresh attempts
5. Observe debouncing (minimum 3s between refreshes)

**Demo Steps - Manual Refresh API**:
```powershell
# Simulate manual refresh via API
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:5000/api/vehicle/refresh"
```

**Expected Behavior**:
- Auto-refresh every 60 seconds when page visible
- Pull gesture triggers manual refresh
- Debouncing prevents refresh spam
- Loading indicator shows during refresh

---

## Settings & User Preferences (Phase 8)

**Goal**: Configure distance and temperature units

**Demo Steps**:
1. Navigate to `/settings`
2. Change "Distance Units" to "Miles (mi)"
3. Change "Temperature Units" to "Fahrenheit (°F)"
4. Click "Save Settings"
5. Observe success message
6. Return to home screen
7. Verify range shows "217 mi" instead of "350 km"
8. Verify temperature shows "72°F" instead of "22°C"

**Expected Behavior**:
- Settings persist across sessions (JSON file)
- Changes apply immediately after save
- Preferences affect all displays

---

## Error Handling & Edge Cases (Phase 9)

**Goal**: Graceful degradation with offline/error scenarios

**Demo Steps - Stale Data**:
```powershell
$env:MOCK_SCENARIO = "stale_data"
# Restart Flask - observe "90s ago" with stale indicator
```

**Demo Steps - Network Failure**:
```powershell
# Simulate 100% failure rate
$env:MOCK_DELAY = "0.5"
# Stop Flask server
# Refresh page - observe error banner: "Unable to reach vehicle"
# Cached data displayed with warning
```

**Demo Steps - Low Battery Warning**:
```powershell
$env:MOCK_SCENARIO = "low_battery"
# Amber warning indicator on battery card
```

**Demo Steps - Critical Battery Warning**:
```powershell
$env:MOCK_SCENARIO = "critical_battery"
# Red banner: "Critical battery level! Charge immediately."
```

**Expected Behavior**:
- Network errors show cached data with banner
- Stale data highlighted with border
- Critical warnings persist until resolved
- Graceful fallback to defaults

---

## Constitution Compliance Verification

### ✅ Principle I: Security-First Development
- No sensitive data in code (using environment variables)
- Atomic writes with file locking for data integrity

### ✅ Principle II: Performance Excellence
- Mock delays configurable (default 0.5s)
- Debounced refresh (3s minimum)
- Auto-refresh only when page visible

### ✅ Principle III: User-Centric Design
- Mobile-first responsive design
- Clear visual indicators for all states
- Accessible color schemes (light/dark mode support)

### ✅ Principle IV: Test-Driven Development (NON-NEGOTIABLE)
- 94% test coverage (exceeds 85% requirement)
- 56 unit + integration tests, all passing

### ✅ Principle V: Web-Based Simplicity
- Python Flask backend (no Django/FastAPI)
- Vanilla HTML5/CSS3/JavaScript ES6+ (no frameworks)
- Simple directory structure

### ✅ Principle VI: Mock-First Integration
- VehicleDataMockService with 7 scenarios
- Configurable delays and failure rates
- No external API dependencies

### ✅ Principle VII: Prototype-First Development
- Demo-ready implementation
- All 5 user stories functional
- Visual indicators and animations

### ✅ Principle VIII: Design-Driven Implementation (NON-NEGOTIABLE)
- Classes match UML class diagram exactly
- VehicleState, UserProfile, HomeScreenPresenter per spec
- Enums: UnitSystem, TempUnit, LockStatus

---

## Performance Metrics

**Page Load Time**: <2s (all assets)
**API Response Time**: 0.5s (configurable mock delay)
**Test Execution**: 1.93s (56 tests)
**Coverage**: 94% (642 statements, 40 missed)
**Flake8 Errors**: 0 critical errors

---

## Demo Checklist

- [ ] US1: Battery percentage displays correctly
- [ ] US1: Range estimate shows in preferred units
- [ ] US1: Low battery warning (amber at <20%)
- [ ] US1: Critical battery banner (red at <5%)
- [ ] US2: Lock status displays with icon
- [ ] US2: Unlocked warning (amber at >10 min)
- [ ] US3: Cabin temperature in preferred units
- [ ] US3: Climate On/Off status with animation
- [ ] US4: Vehicle SVG displays and scales
- [ ] US5: Auto-refresh every 60s
- [ ] US5: Pull-to-refresh gesture works
- [ ] US5: Debouncing prevents spam
- [ ] Settings: Unit preferences persist
- [ ] Error: Cached data shows on failure
- [ ] Error: Stale data indicator shows

---

## Next Steps (Production Readiness)

**Not Implemented (Out of Scope for Prototype)**:
- Real vehicle API integration
- User authentication
- Database persistence
- Production WSGI server
- HTTPS/TLS
- Monitoring/logging
- Rate limiting
- API versioning

**To Deploy to Production**:
1. Replace VehicleDataMockService with real API client
2. Add user authentication (Flask-Login)
3. Use PostgreSQL instead of JSON files
4. Deploy with Gunicorn + Nginx
5. Enable HTTPS with Let's Encrypt
6. Add monitoring (Prometheus + Grafana)
7. Implement rate limiting (Flask-Limiter)
8. Add comprehensive error logging

---

## Troubleshooting

**Issue**: Flask server won't start
- **Fix**: Ensure virtual environment activated, dependencies installed

**Issue**: Tests fail on Windows
- **Fix**: File locking uses msvcrt (Windows-specific module)

**Issue**: Coverage below 85%
- **Fix**: Already at 94%, no action needed

**Issue**: API returns 503
- **Fix**: Check MOCK_SCENARIO environment variable, ensure valid scenario name

**Issue**: Pull-to-refresh not working
- **Fix**: Feature requires touch events (mobile device or DevTools device mode)

---

**Demo Complete!** All 5 user stories demonstrated with test coverage validation.
