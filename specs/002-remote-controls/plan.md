# Implementation Plan: Remote Controls Feature (FR-RMC)

**Feature**: 002-remote-controls  
**Based on**: `spec.md` (6 user stories, 10 SRS requirements)  
**Target Completion**: 5 weeks  
**Status**: Planning

---

## Executive Summary

This plan outlines the implementation of remote vehicle control features including lock/unlock, climate control, heated seats/steering, defrost, trunk/frunk opening, and vehicle location (honk & flash).

**Scope**: All FR-RMC requirements (FR-RMC-001 through FR-RMC-010)  
**Priority**: High (P1) - Core user-facing features  
**Dependencies**: Home Screen feature (001) complete ✅

---

## Constitution Compliance Check

| Principle | Compliance | Notes |
|-----------|-----------|-------|
| **I. Security-First** | ✅ Pass | All commands require authentication, TLS encryption, audit logging |
| **II. Performance Excellence** | ✅ Pass | Command response <3s, optimistic UI, retry logic |
| **III. User-Centric Design** | ✅ Pass | 1-tap access, clear feedback, safety warnings |
| **IV. Test-Driven Development** | ✅ Pass | ≥85% coverage target, unit + integration tests |
| **V. Web-Based Simplicity** | ✅ Pass | Flask + vanilla JS, RESTful API |
| **VI. Mock-First Integration** | ✅ Pass | RemoteCommandMockService with realistic delays |
| **VII. Prototype-First** | ✅ Pass | Demo-ready with all 6 user stories functional |
| **VIII. Design-Driven** | ✅ Pass | Extend existing UML models, maintain architecture |

**Result**: ✅ All 8 principles satisfied

---

## Technical Architecture

### Backend Extensions

**New Models** (`models/`):
```python
# remote_command.py
class RemoteCommand:
    command_id: UUID
    command_type: CommandType  # Enum
    parameters: Dict
    status: CommandStatus  # Enum
    timestamp: DateTime
    response_time: int  # milliseconds
    error_message: Optional[str]

# climate_settings.py
class ClimateSettings:
    is_active: bool
    target_temp_celsius: float
    front_left_seat_heat: SeatHeatLevel  # Enum
    front_right_seat_heat: SeatHeatLevel
    rear_seat_heat: SeatHeatLevel
    steering_wheel_heat: bool
    front_defrost: bool
    rear_defrost: bool
    is_plugged_in: bool

# trunk_status.py
class TrunkStatus:
    front_trunk_open: bool
    rear_trunk_open: bool

# Enums
class CommandType(Enum):
    LOCK, UNLOCK, CLIMATE_ON, CLIMATE_OFF, SET_TEMP,
    SEAT_HEAT, STEERING_HEAT, DEFROST, TRUNK_OPEN,
    FRUNK_OPEN, HONK_FLASH

class CommandStatus(Enum):
    PENDING, SUCCESS, FAILED, TIMEOUT

class SeatHeatLevel(Enum):
    OFF, LOW, MEDIUM, HIGH
```

**New Services** (`services/`):
```python
# remote_command_service.py
class RemoteCommandService(ABC):
    @abstractmethod
    def send_command(self, command: RemoteCommand) -> RemoteCommand
    
    @abstractmethod
    def get_command_status(self, command_id: UUID) -> RemoteCommand
    
    @abstractmethod
    def cancel_command(self, command_id: UUID) -> bool

# command_queue.py
class CommandQueue:
    def enqueue(self, command: RemoteCommand)
    def dequeue(self) -> Optional[RemoteCommand]
    def get_pending(self) -> List[RemoteCommand]
```

**Mock Implementation** (`mocks/`):
```python
# remote_command_mock.py
class RemoteCommandMockService(RemoteCommandService):
    - Simulates command execution with delays (1-3s)
    - Configurable success/failure rates
    - Realistic state changes (lock → locked, climate → active)
    - Battery drain simulation for climate commands
```

**Updated VehicleState** (`models/vehicle_state.py`):
```python
# Add to existing VehicleState
@dataclass
class VehicleState:
    # ... existing fields ...
    climate_settings: ClimateSettings
    trunk_status: TrunkStatus
    is_plugged_in: bool
```

### Frontend Extensions

**New Page** (`templates/controls.html`):
- Remote controls dashboard
- Lock/Unlock toggle
- Climate control card
- Heated seats/steering controls
- Defrost toggles
- Trunk/Frunk buttons
- Honk & Flash button

**New JavaScript** (`static/js/controls.js`):
- Command execution logic
- Real-time status updates
- Optimistic UI updates
- Error handling and retry
- Haptic feedback integration

**New CSS** (`static/css/controls.css`):
- Control button styles
- Temperature slider
- Loading/success/error states
- Responsive layout

### API Endpoints

**New Routes** (`app.py`):
```python
POST /api/vehicle/lock          # Lock doors
POST /api/vehicle/unlock        # Unlock doors
POST /api/vehicle/climate       # Start/stop climate
PUT  /api/vehicle/climate       # Update climate settings
POST /api/vehicle/trunk/open    # Open trunk
POST /api/vehicle/frunk/open    # Open frunk
POST /api/vehicle/honk-flash    # Honk & flash
GET  /api/vehicle/commands      # Get command history
GET  /api/vehicle/commands/:id  # Get command status
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Goal**: Set up models, services, and mock infrastructure

**Tasks**:
1. Create RemoteCommand model with enums
2. Create ClimateSettings model
3. Create TrunkStatus model
4. Extend VehicleState with new fields
5. Create RemoteCommandService interface
6. Implement RemoteCommandMockService
7. Create CommandQueue for sequential execution
8. Add command history persistence
9. Write unit tests for models
10. Write unit tests for mock service

**Deliverable**: Backend foundation ready for command execution

---

### Phase 2: Lock/Unlock (Week 2 - US1, P1)

**Goal**: Implement remote lock/unlock with haptic feedback

**Tasks**:
1. Create Flask endpoints: POST /lock, POST /unlock
2. Implement lock/unlock in mock service
3. Update home screen to show command feedback
4. Create controls page route: GET /controls
5. Build controls.html template
6. Create lock/unlock UI component
7. Implement controls.js with lock/unlock logic
8. Add haptic feedback (navigator.vibrate)
9. Add optimistic UI updates
10. Write integration tests for lock/unlock
11. Add error handling and retry logic
12. Test command timeout scenarios

**Deliverable**: Working lock/unlock with haptic feedback ✅ US1

---

### Phase 3: Climate Control (Week 2-3 - US2, P1)

**Goal**: Remote climate activation with temperature control

**Tasks**:
1. Create Flask endpoints: POST /climate, PUT /climate
2. Implement climate commands in mock service
3. Build climate control UI card
4. Create temperature slider component
5. Implement climate on/off toggle
6. Add temperature presets (18°C, 21°C, 24°C)
7. Calculate battery drain estimates
8. Show warning if not plugged in
9. Update home screen climate indicator
10. Write tests for climate commands
11. Add temperature unit conversion
12. Test climate state synchronization

**Deliverable**: Working climate control with warnings ✅ US2

---

### Phase 4: Advanced Climate Features (Week 3 - US3 & US4, P2)

**Goal**: Heated seats, steering wheel, and defrost controls

**Tasks US3 (Heated Seats/Steering)**:
1. Add seat heat controls to climate card
2. Create seat heat level selector (Off/Low/Med/High)
3. Implement heated steering wheel toggle
4. Add seat heat icons (visual indicators)
5. Update mock service with seat heat state
6. Write tests for seat heat commands

**Tasks US4 (Defrost)**:
7. Add defrost controls to climate card
8. Implement front defrost toggle
9. Implement rear defrost toggle
10. Add 15-minute auto-shutoff timer
11. Update mock service with defrost state
12. Write tests for defrost commands

**Deliverable**: Advanced climate features working ✅ US3, US4

---

### Phase 5: Trunk/Frunk & Locate (Week 4 - US5 & US6, P2/P3)

**Goal**: Remote trunk/frunk opening and honk & flash

**Tasks US5 (Trunk/Frunk)**:
1. Create Flask endpoints: POST /trunk/open, POST /frunk/open
2. Implement trunk/frunk commands in mock service
3. Build trunk/frunk UI card
4. Add confirmation dialogs
5. Add safety check (reject if moving)
6. Show trunk/frunk open indicators
7. Write tests for trunk/frunk commands

**Tasks US6 (Honk & Flash)**:
8. Create Flask endpoint: POST /honk-flash
9. Implement honk & flash in mock service
10. Build locate vehicle button
11. Add cooldown timer (10s between uses)
12. Show visual feedback (honking animation)
13. Write tests for honk & flash

**Deliverable**: All 6 user stories complete ✅ US5, US6

---

### Phase 6: Polish & Testing (Week 5)

**Goal**: Achieve ≥85% coverage, optimize performance, polish UI

**Tasks**:
1. Write comprehensive unit tests for all models
2. Write integration tests for all API endpoints
3. Test command queue and retry logic
4. Test all error scenarios
5. Test offline mode behavior
6. Optimize command response times
7. Add loading animations
8. Polish UI transitions
9. Add success/error toast notifications
10. Test haptic feedback on devices
11. Verify temperature conversions
12. Code review and flake8 validation
13. Performance profiling
14. Update README and DEMO docs

**Deliverable**: Production-ready feature with ≥85% coverage

---

## Project Structure

```
SE_Project/
├── models/
│   ├── remote_command.py       # NEW
│   ├── climate_settings.py     # NEW
│   ├── trunk_status.py         # NEW
│   ├── vehicle_state.py        # EXTENDED
│   └── enums.py               # EXTENDED (new enums)
├── services/
│   ├── remote_command_service.py  # NEW
│   └── command_queue.py          # NEW
├── mocks/
│   └── remote_command_mock.py    # NEW
├── static/
│   ├── css/
│   │   └── controls.css          # NEW
│   ├── js/
│   │   └── controls.js           # NEW
│   └── images/
│       └── control-icons.svg     # NEW (lock, climate, etc.)
├── templates/
│   └── controls.html             # NEW
├── tests/
│   ├── unit/
│   │   ├── test_remote_command.py      # NEW
│   │   ├── test_climate_settings.py    # NEW
│   │   └── test_command_mock.py        # NEW
│   └── integration/
│       └── test_remote_controls_api.py # NEW
└── app.py                        # EXTENDED (new routes)
```

---

## Risk Management

### High Priority Risks

**Risk 1: Command Timeout Issues**
- **Impact**: High (user frustration)
- **Mitigation**: 
  - Implement retry logic (max 3 attempts)
  - Clear timeout messages
  - Optimistic UI updates
  - Queue pending commands

**Risk 2: Battery Drain Concerns**
- **Impact**: Medium (user anxiety)
- **Mitigation**:
  - Prominent warnings when not plugged in
  - Show estimated range reduction
  - Disable climate if battery <10%
  - Clear "plugged in" indicators

**Risk 3: Conflicting Commands**
- **Impact**: Medium (unexpected behavior)
- **Mitigation**:
  - Command queue (sequential execution)
  - Disable buttons during command execution
  - Show "Command in progress..." message
  - Cancel previous pending commands

**Risk 4: Safety Issues (Trunk While Moving)**
- **Impact**: High (safety concern)
- **Mitigation**:
  - Server-side validation
  - Reject commands if vehicle speed >0
  - Clear error messages
  - Log rejected commands for audit

---

## Testing Strategy

### Unit Tests (Target: 50+ tests)

**Models**:
- RemoteCommand creation and validation
- ClimateSettings temperature range validation
- Enum conversions and edge cases
- VehicleState serialization with new fields

**Services**:
- RemoteCommandMockService command execution
- Command success/failure scenarios
- CommandQueue enqueue/dequeue
- Retry logic and timeout handling

**Coverage Target**: ≥85% for new code

### Integration Tests (Target: 20+ tests)

**API Endpoints**:
- Lock/unlock command flow
- Climate control with all parameters
- Trunk/frunk opening with safety checks
- Honk & flash cooldown enforcement
- Command status polling
- Error response validation

**End-to-End Scenarios**:
- Complete climate preconditioning flow
- Lock → Unlock → Lock sequence
- Command queue with multiple pending commands
- Timeout and retry scenarios

### Performance Tests

**Benchmarks**:
- Command response time <3s (lock/unlock)
- Command response time <5s (climate)
- API endpoint latency <500ms
- UI responsiveness <100ms

---

## Success Metrics

### Functional Completeness
- ✅ All 6 user stories implemented
- ✅ All 10 SRS requirements satisfied
- ✅ All acceptance criteria met

### Quality Gates
- ✅ Test coverage ≥85%
- ✅ All tests passing
- ✅ Zero critical flake8 errors
- ✅ Command success rate ≥99%

### Performance Targets
- ✅ Lock/unlock response <3s
- ✅ Climate response <5s
- ✅ Page load time <2s
- ✅ Haptic feedback <100ms

### User Experience
- ✅ Clear visual feedback for all states
- ✅ Intuitive temperature slider
- ✅ Safety warnings prominent
- ✅ Responsive on mobile devices

---

## Dependencies & Prerequisites

### Technical Prerequisites
- ✅ Flask backend running
- ✅ Python 3.11+ virtual environment
- ✅ VehicleState model exists
- ✅ Mock service infrastructure

### Feature Dependencies
- ✅ Home Screen (001) complete
- ✅ User preferences working
- ✅ Data persistence layer ready
- ✅ API client utilities available

### External Dependencies
- Navigator.vibrate API (haptic feedback)
- Touch events for mobile sliders
- CSS Grid/Flexbox support

---

## Timeline & Milestones

| Week | Phase | Deliverable | Status |
|------|-------|-------------|--------|
| **Week 1** | Foundation | Models, services, mocks ready | 🔜 Next |
| **Week 2** | Lock/Unlock + Climate | US1 & US2 complete (P1) | Pending |
| **Week 3** | Advanced Climate | US3 & US4 complete (P2) | Pending |
| **Week 4** | Trunk & Locate | US5 & US6 complete | Pending |
| **Week 5** | Testing & Polish | ≥85% coverage, production-ready | Pending |

**Estimated Total Effort**: ~120 hours (5 weeks × 24 hours/week)

---

## Out of Scope (Future Features)

The following are explicitly **not included** in this implementation:

❌ Command scheduling (e.g., "Start climate at 7 AM")  
❌ Geofence-based auto-lock/unlock  
❌ Valet mode controls  
❌ Speed limit enforcement UI  
❌ Window control (not in SRS)  
❌ Real vehicle API integration (mock-only prototype)  
❌ Push notifications for command completion  
❌ Command history UI page  
❌ Undo/cancel command feature  

These may be considered for future releases.

---

## Technical Decisions & Rationale

### Decision 1: Command Queue vs Parallel Execution
**Choice**: Sequential command queue  
**Rationale**: 
- Prevents conflicting commands (e.g., lock + unlock simultaneously)
- Simplifies state management
- Matches real vehicle behavior (one command at a time)
- Easier to test and debug

### Decision 2: Optimistic UI Updates
**Choice**: Update UI immediately, rollback on failure  
**Rationale**:
- Better perceived performance
- Reduces user wait time
- Clear rollback on errors
- Industry standard pattern (Tesla, Rivian apps)

### Decision 3: Temperature Slider vs Buttons
**Choice**: Slider with preset buttons  
**Rationale**:
- Intuitive on mobile (touch-friendly)
- Quick presets for common temperatures
- Precise control available
- Follows user-centric design principle

### Decision 4: Haptic Feedback Only for Lock/Unlock
**Choice**: Vibration feedback for lock/unlock success only  
**Rationale**:
- High-value security confirmation
- SRS requirement (FR-RMC-010)
- Avoids notification fatigue
- Consistent with mobile OS patterns

---

## Constitution Alignment Details

### Principle IV: Test-Driven Development (NON-NEGOTIABLE)
- Unit tests written for all models before implementation
- Integration tests define API contracts
- Mock service enables isolated testing
- Coverage enforced at ≥85%

### Principle V: Web-Based Simplicity
- Flask backend (no additional frameworks)
- Vanilla JavaScript (no React/Vue/Angular)
- RESTful API design (no GraphQL/WebSockets complexity)
- Simple HTML templates

### Principle VI: Mock-First Integration
- RemoteCommandMockService with realistic delays
- No real vehicle API required
- Configurable success/failure rates
- Demo-ready without external dependencies

### Principle VIII: Design-Driven Implementation (NON-NEGOTIABLE)
- Extend existing architecture (no rewrites)
- Follow established patterns from Home Screen feature
- Maintain consistency with VehicleState model
- UML-compliant class design

---

## Acceptance Criteria

This implementation plan is approved when:

- [x] All 6 user stories mapped to implementation tasks
- [x] Technical architecture defined
- [x] 5-phase timeline established
- [x] Risk mitigation strategies documented
- [x] Testing strategy comprehensive
- [x] Constitution compliance verified (8/8)
- [ ] Stakeholder review complete
- [ ] Ready for task breakdown

**Status**: ✅ Ready for `/speckit.tasks`

---

## Next Steps

1. **Generate Task Breakdown**: Run `/speckit.tasks` to create detailed task list (85-100 tasks)
2. **Begin Implementation**: Start with Phase 1 (Foundation)
3. **Iterative Development**: Complete one phase at a time
4. **Continuous Testing**: Write tests alongside implementation
5. **Regular Commits**: Commit after each completed task or logical unit

**Ready to proceed**: ✅ Yes - plan approved
