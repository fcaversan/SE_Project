# Phase 3: Charging Management - Technical Specification

## Overview
Implementation of charging management features including remote charging control, charge limit settings, scheduling, and charging station locator.

## SRS Requirements Coverage

### FR-CHG: Charging Management (8 requirements)

- **FR-CHG-001**: Start charging session remotely
- **FR-CHG-002**: Stop charging session remotely
- **FR-CHG-003**: Display charging session details (SoC, time remaining, rate, voltage/amperage)
- **FR-CHG-004**: Set charge limit (default 80%, one-time 100% option)
- **FR-CHG-005**: Create/edit/delete charging schedules
- **FR-CHG-006**: Display charging station map
- **FR-CHG-007**: Filter charging stations by connector/power
- **FR-CHG-008**: Show real-time station availability

## Architecture

### Data Models

#### ChargingSession
```python
@dataclass
class ChargingSession:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    start_soc: float
    current_soc: float
    target_soc: float
    charging_rate_kw: float
    voltage: float
    amperage: float
    energy_added_kwh: float
    cost: float
    location: str
    is_active: bool
```

#### ChargingSchedule
```python
@dataclass
class ChargingSchedule:
    schedule_id: str
    name: str
    enabled: bool
    days_of_week: List[int]  # 0-6 for Mon-Sun
    start_time: Optional[str]  # "HH:MM" or None for ready-by
    ready_by_time: Optional[str]  # "HH:MM" or None for start
    target_soc: int  # Percentage
```

#### ChargingStation
```python
@dataclass
class ChargingStation:
    station_id: str
    name: str
    latitude: float
    longitude: float
    connector_types: List[str]  # ["CCS", "CHAdeMO", "Tesla"]
    power_levels_kw: List[int]  # [50, 150, 250]
    available_stalls: int
    total_stalls: int
    is_operational: bool
    cost_per_kwh: float
```

### Backend Components

#### Services
1. **ChargingService** - Interface for charging operations
2. **ChargingMockService** - Mock implementation with simulated charging
3. **ChargingStationService** - Manages charging station data
4. **ScheduleService** - Manages charging schedules

#### API Endpoints
```
POST   /api/charging/start          - Start charging
POST   /api/charging/stop           - Stop charging
GET    /api/charging/status         - Get current session
GET    /api/charging/history        - Get charging history
PUT    /api/charging/limit          - Set charge limit
GET    /api/charging/schedules      - List schedules
POST   /api/charging/schedules      - Create schedule
PUT    /api/charging/schedules/<id> - Update schedule
DELETE /api/charging/schedules/<id> - Delete schedule
GET    /api/charging/stations       - Get nearby stations
GET    /api/charging/stations/map   - Get station map data
```

### Frontend Components

#### Pages
1. **Charging Page** (`/charging`)
   - Current session status
   - Start/stop controls
   - Charge limit slider
   - Charging history

2. **Charging Stations Page** (`/charging/stations`)
   - Map view with station markers
   - List view with filters
   - Station details

#### UI Components
1. **ChargingStatusCard** - Shows active session details
2. **ChargeLimitControl** - Slider + quick actions (80%, 100%)
3. **ScheduleManager** - Create/edit schedules
4. **StationMap** - Interactive map with markers
5. **StationList** - Filterable list of stations
6. **ChargingHistoryChart** - Historical charging sessions

### State Management
```javascript
// Charging state
{
    isCharging: boolean,
    currentSession: ChargingSession | null,
    chargeLimit: number,
    schedules: ChargingSchedule[],
    chargingHistory: ChargingSession[],
    nearbyStations: ChargingStation[]
}
```

## Mock Service Implementation

### Charging Simulation
- Simulate realistic charging curves (fast initial, then tapers)
- Different rates for L2 (11kW) vs DC Fast (150kW)
- Calculate estimated time based on current SoC and target
- Simulate voltage/amperage variations

### Station Data
- Generate mock stations around vehicle location
- Simulate availability changes over time
- Different connector types and power levels
- Pricing variations

## UI/UX Design

### Charging Page Layout
```
┌─────────────────────────────────────┐
│ ← Charging                          │
├─────────────────────────────────────┤
│                                     │
│  ⚡ Charging Status                │
│  ┌───────────────────────────────┐ │
│  │ ● Charging                    │ │
│  │ 67% → 80%                     │ │
│  │ ████████████░░░░░░            │ │
│  │                               │ │
│  │ 45 min remaining              │ │
│  │ 48 kW • 400V • 120A          │ │
│  │                               │ │
│  │ [Stop Charging]               │ │
│  └───────────────────────────────┘ │
│                                     │
│  🎯 Charge Limit                   │
│  ┌───────────────────────────────┐ │
│  │ 80%                           │ │
│  │ ●─────────────────────○      │ │
│  │ [80%] [90%] [100%]           │ │
│  └───────────────────────────────┘ │
│                                     │
│  ⏰ Schedules                      │
│  [+ New Schedule]                  │
│  ┌───────────────────────────────┐ │
│  │ Weeknight Charging            │ │
│  │ Mon-Fri • Ready by 7:00 AM   │ │
│  │ Target: 80%         [Edit]   │ │
│  └───────────────────────────────┘ │
│                                     │
│  📍 [Find Charging Stations]       │
│                                     │
│  📊 Charging History               │
└─────────────────────────────────────┘
```

### Charging Stations Page
```
┌─────────────────────────────────────┐
│ ← Charging Stations                 │
├─────────────────────────────────────┤
│  [Map View] [List View]             │
│                                     │
│  Filters:                           │
│  [All] [CCS] [CHAdeMO] [Tesla]     │
│  [All] [50kW] [150kW] [250kW]      │
│                                     │
│  ┌─────────────────────────────┐   │
│  │       🗺️ Map View          │   │
│  │                             │   │
│  │   📍  📍     📍            │   │
│  │        📍  📍              │   │
│  │   📍              📍       │   │
│  │                             │   │
│  └─────────────────────────────┘   │
│                                     │
│  Supercharger Downtown              │
│  ⚡ 8/12 available • 150 kW         │
│  📍 0.5 mi away          [Navigate]│
│                                     │
│  Tesla Supercharger Main St         │
│  ⚡ 12/16 available • 250 kW        │
│  📍 1.2 mi away          [Navigate]│
└─────────────────────────────────────┘
```

## Testing Strategy

### Unit Tests
- ChargingSession model serialization
- Schedule validation logic
- Charge limit constraints (0-100%)
- Charging rate calculations
- Time estimation algorithms

### Integration Tests
- Start/stop charging API
- Charge limit update
- Schedule CRUD operations
- Station filtering
- Historical data retrieval

### Test Scenarios
1. Start charging when plugged in
2. Reject charging when not plugged in
3. Stop active charging session
4. Set charge limit and respect it
5. Create daily charging schedule
6. Edit schedule times
7. Delete schedule
8. Filter stations by connector type
9. Calculate estimated time remaining
10. Charging history with costs

## Implementation Phases

### Phase 3.1: Core Charging Control (FR-CHG-001, 002, 003)
- Data models
- Mock service
- API endpoints
- UI for start/stop
- Real-time status display

### Phase 3.2: Charge Limits (FR-CHG-004)
- Charge limit model
- Limit control UI
- Quick actions (80%, 100%)
- Persist user preference

### Phase 3.3: Scheduling (FR-CHG-005)
- Schedule model
- Schedule service
- Schedule manager UI
- Schedule execution logic

### Phase 3.4: Charging Stations (FR-CHG-006, 007, 008)
- Station data model
- Station service
- Map integration
- Filtering and search
- Availability display

## Success Criteria

- ✅ Can start/stop charging remotely
- ✅ Real-time charging status updates
- ✅ Charge limit respected
- ✅ Schedules trigger at correct times
- ✅ Station map displays locations
- ✅ Filters work correctly
- ✅ All 8 FR-CHG requirements implemented
- ✅ All tests passing
- ✅ UI responsive and intuitive
