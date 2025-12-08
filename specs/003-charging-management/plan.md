# Phase 3: Charging Management - Implementation Plan

## Overview
Build charging management features following TDD approach with mock services.

## Implementation Order

### Step 1: Data Models & Enums
**Files to create/modify:**
- `models/charging_session.py` - ChargingSession model
- `models/charging_schedule.py` - ChargingSchedule model
- `models/charging_station.py` - ChargingStation model
- `models/enums.py` - Add ChargingStatus, ConnectorType enums

**Tasks:**
1. Create ChargingSession with all fields
2. Create ChargingSchedule with validation
3. Create ChargingStation model
4. Add to_dict/from_dict methods
5. Write unit tests for serialization

**Tests:** `tests/unit/test_charging_models.py`

---

### Step 2: Mock Charging Service
**Files to create:**
- `mocks/charging_mock.py` - ChargingMockService
- `services/charging_service.py` - Abstract base class

**Features:**
- Simulate charging curves (fast start, taper off)
- Different rates for L2 (11kW) vs DC Fast (150-250kW)
- Calculate time remaining
- Persist charging sessions
- Generate mock station data

**Tasks:**
1. Define abstract ChargingService interface
2. Implement ChargingMockService
3. Add charging simulation logic
4. Add persistence for sessions
5. Write unit tests

**Tests:** `tests/unit/test_charging_mock.py`

---

### Step 3: Backend API Endpoints
**Files to modify:**
- `app.py` - Add charging endpoints

**Endpoints:**
```python
# Charging control
POST   /api/charging/start
POST   /api/charging/stop
GET    /api/charging/status

# Charge limit
GET    /api/charging/limit
PUT    /api/charging/limit

# Schedules
GET    /api/charging/schedules
POST   /api/charging/schedules
PUT    /api/charging/schedules/<id>
DELETE /api/charging/schedules/<id>

# Stations
GET    /api/charging/stations
```

**Tasks:**
1. Initialize charging service
2. Implement each endpoint
3. Add error handling
4. Add request validation
5. Write integration tests

**Tests:** `tests/integration/test_charging_api.py`

---

### Step 4: Frontend - Charging Page
**Files to create:**
- `templates/charging.html` - Main charging page
- `static/css/charging.css` - Charging styles
- `static/js/charging.js` - Charging logic

**Components:**
1. **Charging Status Card**
   - Current SoC progress
   - Target SoC
   - Time remaining
   - Power/voltage/amperage
   - Start/stop button

2. **Charge Limit Control**
   - Slider (0-100%)
   - Quick buttons (80%, 90%, 100%)
   - Save button

3. **Charging History**
   - List of past sessions
   - Date, duration, energy added, cost

**Tasks:**
1. Create HTML structure
2. Style components
3. Implement JavaScript logic
4. Add real-time status updates
5. Handle start/stop actions

---

### Step 5: Schedule Manager
**Files to create/modify:**
- `templates/charging.html` - Add schedule section
- `static/js/charging.js` - Add schedule functions
- `services/schedule_service.py` - Schedule execution

**Features:**
- Create new schedule
- Edit existing schedule
- Delete schedule
- Enable/disable schedule
- Days of week selection
- Start time OR ready-by time
- Target SoC

**Tasks:**
1. Create schedule UI components
2. Implement CRUD operations
3. Add schedule validation
4. Create schedule service
5. Write tests

**Tests:** `tests/unit/test_schedule_service.py`

---

### Step 6: Charging Stations
**Files to create:**
- `templates/stations.html` - Stations page
- `static/css/stations.css` - Stations styles
- `static/js/stations.js` - Stations logic
- `mocks/charging_stations_mock.py` - Mock station data

**Features:**
- Map view with markers
- List view
- Filter by connector type
- Filter by power level
- Show availability
- Distance from vehicle
- Navigation button

**Tasks:**
1. Generate mock station data
2. Create stations page
3. Implement map (simple CSS or integrate map library)
4. Add filtering
5. Style station cards

---

### Step 7: Integration & Polish
**Tasks:**
1. Add navigation from home screen
2. Update home screen with charging status
3. Add notifications for charging complete
4. Handle edge cases
5. Test all user flows
6. Update documentation

---

## Development Workflow

### For Each Feature:
1. **Write Tests First** (TDD)
   - Unit tests for models
   - Unit tests for services
   - Integration tests for APIs
   
2. **Implement Backend**
   - Data models
   - Services
   - API endpoints
   - Run tests, iterate until green
   
3. **Implement Frontend**
   - HTML structure
   - CSS styling
   - JavaScript logic
   - Manual testing
   
4. **Integration Testing**
   - Test end-to-end flows
   - Test error cases
   - Test edge cases
   
5. **Code Review & Commit**
   - Review code
   - Commit with descriptive message
   - Push to branch

---

## Charging Simulation Logic

### Charging Curve
```python
def calculate_charging_rate(current_soc: float, max_rate_kw: float) -> float:
    """Simulate realistic charging curve"""
    if current_soc < 20:
        return max_rate_kw  # Full speed at low SoC
    elif current_soc < 80:
        return max_rate_kw * 0.95  # Slight reduction
    elif current_soc < 90:
        return max_rate_kw * 0.6  # Significant taper
    else:
        return max_rate_kw * 0.3  # Very slow at high SoC
```

### Time Estimation
```python
def estimate_time_remaining(
    current_soc: float,
    target_soc: float,
    battery_capacity_kwh: float,
    charging_rate_kw: float
) -> int:
    """Calculate minutes to reach target SoC"""
    energy_needed = (target_soc - current_soc) / 100 * battery_capacity_kwh
    # Account for charging curve
    avg_rate = charging_rate_kw * 0.8  # Average considering taper
    hours = energy_needed / avg_rate
    return int(hours * 60)
```

---

## Mock Station Data

### Station Types
1. **Supercharger** - 250 kW, Tesla connector
2. **DC Fast Charger** - 150 kW, CCS + CHAdeMO
3. **Level 2** - 11 kW, J1772

### Generated Stations
- 3-5 stations within 5 miles
- Random availability (60-100%)
- Varying power levels
- Different connector types
- Realistic pricing ($0.30-$0.50/kWh)

---

## Data Persistence

### Files
- `data/charging_sessions.json` - Historical sessions
- `data/charging_schedules.json` - User schedules
- `data/charging_preferences.json` - Charge limit, settings

### Structure
```json
{
  "sessions": [
    {
      "session_id": "uuid",
      "start_time": "2025-12-08T10:00:00",
      "end_time": "2025-12-08T11:30:00",
      "start_soc": 25.0,
      "end_soc": 80.0,
      "energy_added_kwh": 45.5,
      "cost": 15.75,
      "location": "Supercharger Downtown"
    }
  ],
  "schedules": [
    {
      "schedule_id": "uuid",
      "name": "Weeknight Charging",
      "enabled": true,
      "days_of_week": [0, 1, 2, 3, 4],
      "ready_by_time": "07:00",
      "target_soc": 80
    }
  ],
  "preferences": {
    "default_charge_limit": 80,
    "charge_limit_override": null
  }
}
```

---

## Error Handling

### Common Errors
1. **Not Plugged In** - Cannot start charging
2. **Already Charging** - Cannot start again
3. **Not Charging** - Cannot stop
4. **Invalid Limit** - Must be 1-100%
5. **Schedule Conflict** - Times overlap
6. **Network Error** - Service unavailable

### User Feedback
- Toast messages for success/error
- Loading states during operations
- Clear error messages
- Retry options for failures

---

## Testing Checklist

### Unit Tests
- ✅ ChargingSession serialization
- ✅ ChargingSchedule validation
- ✅ Charging rate calculation
- ✅ Time estimation
- ✅ Schedule conflict detection

### Integration Tests
- ✅ Start charging (plugged in)
- ✅ Start charging (not plugged in) - should fail
- ✅ Stop charging
- ✅ Update charge limit
- ✅ Create schedule
- ✅ Update schedule
- ✅ Delete schedule
- ✅ Get stations
- ✅ Filter stations

### E2E Scenarios
- ✅ Complete charging session
- ✅ Change limit mid-charge
- ✅ Schedule executes correctly
- ✅ Find and navigate to station

---

## Timeline Estimate

| Task | Estimated Time |
|------|----------------|
| Data Models | 1 hour |
| Mock Service | 2 hours |
| API Endpoints | 2 hours |
| Charging Page | 3 hours |
| Schedule Manager | 2 hours |
| Stations Page | 3 hours |
| Testing | 2 hours |
| Integration | 1 hour |
| **Total** | **16 hours** |

---

## Success Metrics

- ✅ All 8 FR-CHG requirements implemented
- ✅ 100% test coverage for new code
- ✅ No regressions in existing features
- ✅ UI responsive and polished
- ✅ Documentation complete
- ✅ Code reviewed and merged
