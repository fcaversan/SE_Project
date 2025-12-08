# Tasks: Remote Controls Feature (FR-RMC)

**Input**: Design documents from `/specs/002-remote-controls/`  
**Prerequisites**: plan.md ✅, spec.md ✅

**Organization**: Tasks are grouped by phase and user story (US1-US6) to enable systematic implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- File paths reference repository root

---

## Phase 1: Foundation (Week 1)

**Purpose**: Set up models, services, and mock infrastructure for remote command execution

**⚠️ CRITICAL**: This phase must be complete before ANY user story implementation begins

### Models & Data Structures

- [ ] T001 Create CommandType enum in `models/enums.py` (LOCK, UNLOCK, CLIMATE_ON, CLIMATE_OFF, SET_TEMP, SEAT_HEAT, STEERING_HEAT, DEFROST, TRUNK_OPEN, FRUNK_OPEN, HONK_FLASH)
- [ ] T002 Create CommandStatus enum in `models/enums.py` (PENDING, SUCCESS, FAILED, TIMEOUT)
- [ ] T003 Create SeatHeatLevel enum in `models/enums.py` (OFF, LOW, MEDIUM, HIGH)
- [ ] T004 Create RemoteCommand model in `models/remote_command.py` (command_id, command_type, parameters, status, timestamp, response_time, error_message)
- [ ] T005 Create ClimateSettings model in `models/climate_settings.py` (is_active, target_temp_celsius, seat heat levels, steering_wheel_heat, defrost toggles, is_plugged_in)
- [ ] T006 Create TrunkStatus model in `models/trunk_status.py` (front_trunk_open, rear_trunk_open)
- [ ] T007 Extend VehicleState model in `models/vehicle_state.py` to include climate_settings, trunk_status, is_plugged_in fields

### Services & Interfaces

- [ ] T008 Create RemoteCommandService interface in `services/remote_command_service.py` (send_command, get_command_status, cancel_command abstract methods)
- [ ] T009 Create CommandQueue class in `services/command_queue.py` (enqueue, dequeue, get_pending methods for sequential execution)
- [ ] T010 Implement RemoteCommandMockService in `mocks/remote_command_mock.py` (configurable delays 1-3s, success/failure rates, state change simulation)
- [ ] T011 [P] Add command execution simulation logic in mock service (lock→locked, climate→active with battery drain)
- [ ] T012 [P] Add command history persistence in `services/data_persistence.py` (save commands to data/command_history.json)
- [ ] T013 [P] Add battery drain simulation in mock service (climate drains 1-3% per 10 min, stop if <10%)

### Testing Foundation

- [ ] T014 [P] Write unit tests for CommandType, CommandStatus, SeatHeatLevel enums in `tests/unit/test_enums.py`
- [ ] T015 [P] Write unit tests for RemoteCommand model in `tests/unit/test_remote_command.py` (creation, validation, status transitions)
- [ ] T016 [P] Write unit tests for ClimateSettings model in `tests/unit/test_climate_settings.py` (temperature range validation, defaults)
- [ ] T017 [P] Write unit tests for TrunkStatus model in `tests/unit/test_trunk_status.py`
- [ ] T018 [P] Write unit tests for CommandQueue in `tests/unit/test_command_queue.py` (enqueue/dequeue, ordering, empty queue)
- [ ] T019 Write unit tests for RemoteCommandMockService in `tests/unit/test_command_mock.py` (command execution, timeouts, failures)
- [ ] T020 Run all Phase 1 tests and verify ≥85% coverage for new models/services

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 2: Lock/Unlock (Week 2 - US1, Priority 1)

**Purpose**: Implement remote door lock/unlock with haptic feedback (FR-RMC-001, FR-RMC-002, FR-RMC-010)

### Backend API

- [ ] T021 [US1] Create POST /api/vehicle/lock endpoint in `app.py` (validate request, enqueue lock command, return command_id)
- [ ] T022 [US1] Create POST /api/vehicle/unlock endpoint in `app.py` (validate request, enqueue unlock command, return command_id)
- [ ] T023 [US1] Create GET /api/vehicle/commands/:id endpoint in `app.py` (query command status by ID, return RemoteCommand)
- [ ] T024 [US1] Add command execution to RemoteCommandMockService (update lock_status in VehicleState, simulate 1-2s delay)
- [ ] T025 [US1] [P] Add error handling for lock/unlock (reject if vehicle offline, already locked/unlocked)
- [ ] T026 [US1] [P] Add retry logic for failed lock/unlock commands (max 3 attempts, exponential backoff)

### Frontend UI

- [ ] T027 [US1] Create GET /controls route in `app.py` (render controls template)
- [ ] T028 [US1] Create `templates/controls.html` with base layout and navigation back to home
- [ ] T029 [US1] Create `static/css/controls.css` with control button styles, loading states, success/error animations
- [ ] T030 [US1] Create lock/unlock card component in controls.html (two buttons: Lock and Unlock)
- [ ] T031 [US1] Create `static/js/controls.js` with lock/unlock command execution logic
- [ ] T032 [US1] Implement optimistic UI updates (immediately show "Locking..." state, rollback on failure)
- [ ] T033 [US1] Add haptic feedback using navigator.vibrate API (200ms vibration on success, 50ms-50ms-50ms on failure)
- [ ] T034 [US1] Add command status polling (check every 500ms until SUCCESS/FAILED/TIMEOUT)
- [ ] T035 [US1] Add loading spinner animation during command execution
- [ ] T036 [US1] Add success toast notification ("Vehicle locked" with green checkmark)
- [ ] T037 [US1] Add error toast notification ("Failed to lock vehicle" with retry button)

### Integration & Testing

- [ ] T038 [US1] Update home screen to show lock/unlock command feedback (visual indicator when command in progress)
- [ ] T039 [US1] Add navigation link from home screen to controls page
- [ ] T040 [US1] Write integration tests in `tests/integration/test_lock_unlock_api.py` (lock success, unlock success, already locked/unlocked errors)
- [ ] T041 [US1] Write end-to-end test for lock → unlock → lock sequence
- [ ] T042 [US1] Test timeout scenario (mock service delay >5s)
- [ ] T043 [US1] Test offline scenario (mock service returns CONNECTION_ERROR)
- [ ] T044 [US1] Test haptic feedback on mobile device (manual testing)

**Deliverable**: ✅ US1 complete - Lock/Unlock working with haptic feedback

---

## Phase 3: Climate Control (Week 2-3 - US2, Priority 1)

**Purpose**: Remote climate activation with temperature control and battery warnings (FR-RMC-003, FR-RMC-004, FR-RMC-007)

### Backend API

- [ ] T045 [US2] Create POST /api/vehicle/climate endpoint in `app.py` (start/stop climate with parameters)
- [ ] T046 [US2] Create PUT /api/vehicle/climate endpoint in `app.py` (update temperature and settings while running)
- [ ] T047 [US2] Add climate command execution to RemoteCommandMockService (update climate_settings in VehicleState, simulate 2-3s delay)
- [ ] T048 [US2] Implement battery drain calculation (estimate 1-3% per 10 minutes based on temp differential)
- [ ] T049 [US2] Add safety check: reject climate start if battery_percent <10%
- [ ] T050 [US2] Add safety check: show warning if not plugged in and climate start requested

### Frontend UI

- [ ] T051 [US2] Create climate control card component in controls.html (on/off toggle, temperature slider, presets)
- [ ] T052 [US2] Build temperature slider component (range 15-28°C, step 0.5°C)
- [ ] T053 [US2] Add temperature preset buttons (18°C "Cool", 21°C "Comfort", 24°C "Warm")
- [ ] T054 [US2] Implement climate on/off toggle switch
- [ ] T055 [US2] Add climate command execution logic in controls.js (send climate command, poll status)
- [ ] T056 [US2] Display battery drain estimate ("~2% drain per 10 min")
- [ ] T057 [US2] Show prominent warning modal if not plugged in ("Climate will drain battery. Continue?")
- [ ] T058 [US2] Disable climate button if battery <10% (show "Battery too low" message)
- [ ] T059 [US2] Add temperature unit conversion (use user preferences from HomeScreenPresenter)
- [ ] T060 [US2] Update home screen climate indicator (show "Climate active" badge when running)

### Testing

- [ ] T061 [US2] Write integration tests in `tests/integration/test_climate_api.py` (climate on, climate off, set temperature)
- [ ] T062 [US2] Test battery drain calculation accuracy
- [ ] T063 [US2] Test low battery rejection (battery <10%)
- [ ] T064 [US2] Test unplugged warning display
- [ ] T065 [US2] Test temperature unit conversion (Celsius ↔ Fahrenheit)
- [ ] T066 [US2] Test climate state synchronization between home and controls pages

**Deliverable**: ✅ US2 complete - Climate control with battery warnings

---

## Phase 4: Advanced Climate Features (Week 3 - US3 & US4, Priority 2)

**Purpose**: Heated seats, steering wheel, and defrost controls (FR-RMC-005, FR-RMC-006)

### Heated Seats & Steering (US3)

- [ ] T067 [US3] Add seat heat controls to climate card (3 seat selectors: front-left, front-right, rear)
- [ ] T068 [US3] Create seat heat level selector UI (Off/Low/Medium/High buttons with icons)
- [ ] T069 [US3] Implement heated steering wheel toggle switch
- [ ] T070 [US3] Add seat heat icons to `static/images/control-icons.svg` (visual indicators for each level)
- [ ] T071 [US3] Implement seat heat command execution in controls.js (send SEAT_HEAT command with parameters)
- [ ] T072 [US3] Update RemoteCommandMockService to handle seat heat commands (update climate_settings.front_left_seat_heat etc.)
- [ ] T073 [US3] Display current seat heat levels on home screen climate indicator
- [ ] T074 [US3] Write integration tests in `tests/integration/test_seat_heat_api.py` (set seat heat levels, steering wheel on/off)
- [ ] T075 [US3] Test seat heat state persistence across page navigation

### Defrost (US4)

- [ ] T076 [US4] Add defrost controls to climate card (separate toggles for front and rear)
- [ ] T077 [US4] Implement front defrost toggle switch
- [ ] T078 [US4] Implement rear defrost toggle switch
- [ ] T079 [US4] Add 15-minute auto-shutoff timer for defrost (frontend timer countdown)
- [ ] T080 [US4] Display defrost timer countdown ("Front defrost: 12 min remaining")
- [ ] T081 [US4] Implement defrost command execution in controls.js (send DEFROST command)
- [ ] T082 [US4] Update RemoteCommandMockService to handle defrost commands (update climate_settings.front_defrost, rear_defrost)
- [ ] T083 [US4] Add defrost auto-shutoff in mock service (after 15 minutes)
- [ ] T084 [US4] Write integration tests in `tests/integration/test_defrost_api.py` (front defrost on/off, rear defrost, auto-shutoff)
- [ ] T085 [US4] Test defrost timer accuracy and auto-shutoff behavior

**Deliverable**: ✅ US3 & US4 complete - Advanced climate features working

---

## Phase 5: Trunk/Frunk & Locate (Week 4 - US5 & US6, Priority 2/3)

**Purpose**: Remote trunk/frunk opening and vehicle location (FR-RMC-008, FR-RMC-009)

### Trunk/Frunk Opening (US5)

- [ ] T086 [US5] Create POST /api/vehicle/trunk/open endpoint in `app.py` (open rear trunk)
- [ ] T087 [US5] Create POST /api/vehicle/frunk/open endpoint in `app.py` (open front trunk)
- [ ] T088 [US5] Add trunk/frunk commands to RemoteCommandMockService (update trunk_status, simulate 1-2s delay)
- [ ] T089 [US5] Add safety check: reject trunk/frunk open if vehicle speed >0 mph
- [ ] T090 [US5] Build trunk/frunk UI card in controls.html (two buttons: "Open Trunk", "Open Frunk")
- [ ] T091 [US5] Add confirmation dialog for trunk/frunk ("Open rear trunk? Cannot be closed remotely.")
- [ ] T092 [US5] Implement trunk/frunk command execution in controls.js
- [ ] T093 [US5] Show trunk/frunk open indicators on home screen (visual badge "Trunk Open")
- [ ] T094 [US5] Write integration tests in `tests/integration/test_trunk_api.py` (trunk open, frunk open, moving rejection)
- [ ] T095 [US5] Test safety validation (reject if vehicle moving)

### Honk & Flash (US6)

- [ ] T096 [US6] Create POST /api/vehicle/honk-flash endpoint in `app.py` (honk horn and flash lights)
- [ ] T097 [US6] Add honk & flash command to RemoteCommandMockService (log event, simulate 1s delay)
- [ ] T098 [US6] Build locate vehicle button in controls.html ("Find My Vehicle" with icon)
- [ ] T099 [US6] Implement cooldown timer (10 seconds between honk & flash uses)
- [ ] T100 [US6] Display cooldown countdown ("Wait 7s before next use")
- [ ] T101 [US6] Show visual feedback (honking animation with sound waves icon)
- [ ] T102 [US6] Implement honk & flash command execution in controls.js
- [ ] T103 [US6] Write integration tests in `tests/integration/test_honk_flash_api.py` (honk success, cooldown enforcement)
- [ ] T104 [US6] Test cooldown timer accuracy

**Deliverable**: ✅ US5 & US6 complete - All 6 user stories implemented

---

## Phase 6: Testing & Polish (Week 5)

**Purpose**: Achieve ≥85% test coverage, optimize performance, polish UI

### Comprehensive Testing

- [ ] T105 Write comprehensive unit tests for all new models (RemoteCommand, ClimateSettings, TrunkStatus, enums)
- [ ] T106 Write unit tests for VehicleState extensions (climate_settings, trunk_status fields)
- [ ] T107 Write integration tests for command queue behavior (sequential execution, pending commands)
- [ ] T108 Write integration tests for all API endpoints (POST /lock, /unlock, /climate, /trunk/open, /frunk/open, /honk-flash)
- [ ] T109 Write integration tests for PUT /climate (update temperature while running)
- [ ] T110 Test all error scenarios (offline, timeout, low battery, already locked/unlocked, moving vehicle)
- [ ] T111 Test retry logic and exponential backoff
- [ ] T112 Test offline mode behavior (commands queued when offline, executed when online)
- [ ] T113 Test command history persistence (save to data/command_history.json, load on app start)
- [ ] T114 Run pytest with coverage report and verify ≥85% coverage for all new code
- [ ] T115 Fix any failing tests or coverage gaps

### Performance Optimization

- [ ] T116 Profile command response times (lock/unlock <3s, climate <5s)
- [ ] T117 Optimize API endpoint latency (<500ms)
- [ ] T118 Optimize UI responsiveness (button clicks <100ms)
- [ ] T119 Test haptic feedback latency (<100ms)
- [ ] T120 Optimize mock service delays (realistic but not excessive)

### UI Polish

- [ ] T121 Add smooth loading animations for all command buttons
- [ ] T122 Polish UI transitions (fade in/out, slide, etc.)
- [ ] T123 Add success/error toast notifications with icons
- [ ] T124 Improve temperature slider design (larger touch target, clear current value)
- [ ] T125 Add control icons to `static/images/control-icons.svg` (lock, unlock, climate, seat, trunk, honk)
- [ ] T126 Test responsive layout on mobile devices (320px - 768px widths)
- [ ] T127 Test dark mode compatibility (use CSS variables from Home Screen)
- [ ] T128 Add accessibility attributes (ARIA labels, keyboard navigation)

### Documentation & Validation

- [ ] T129 Update README.md with Remote Controls feature description and usage instructions
- [ ] T130 Update DEMO.md with Remote Controls demo scenarios
- [ ] T131 Run flake8 validation and fix all errors (line length 100, PEP8 compliance)
- [ ] T132 Run pylint and address high-priority warnings
- [ ] T133 Code review: check constitution compliance (all 8 principles)
- [ ] T134 Code review: verify SRS requirements (FR-RMC-001 through FR-RMC-010)
- [ ] T135 Final testing: run all tests and verify 100% pass rate
- [ ] T136 Final testing: manual UI testing on desktop and mobile
- [ ] T137 Final testing: test all 6 user stories end-to-end
- [ ] T138 Create demo screenshots for controls page
- [ ] T139 Prepare feature summary report (coverage, tests, requirements satisfied)
- [ ] T140 Merge 002-remote-controls branch to main

**Deliverable**: ✅ Production-ready Remote Controls feature with ≥85% coverage

---

## SRS Requirements Traceability

| Requirement | User Story | Tasks | Status |
|-------------|------------|-------|--------|
| FR-RMC-001 | US1 | T021-T044 | 🔜 Ready |
| FR-RMC-002 | US1 | T021-T044 | 🔜 Ready |
| FR-RMC-003 | US2 | T045-T066 | Pending |
| FR-RMC-004 | US2 | T045-T066 | Pending |
| FR-RMC-005 | US3 | T067-T075 | Pending |
| FR-RMC-006 | US4 | T076-T085 | Pending |
| FR-RMC-007 | US2 | T045-T066 | Pending |
| FR-RMC-008 | US5 | T086-T095 | Pending |
| FR-RMC-009 | US6 | T096-T104 | Pending |
| FR-RMC-010 | US1 | T033 | Pending |

**Total SRS Coverage**: 10/10 requirements mapped (100%)

---

## Task Summary

**Total Tasks**: 140  
**By Phase**:
- Phase 1 (Foundation): 20 tasks
- Phase 2 (Lock/Unlock): 24 tasks
- Phase 3 (Climate): 22 tasks
- Phase 4 (Advanced Climate): 19 tasks
- Phase 5 (Trunk/Locate): 19 tasks
- Phase 6 (Testing/Polish): 36 tasks

**By Priority**:
- P1 (US1, US2): 46 tasks
- P2 (US3, US4, US5): 38 tasks
- P3 (US6): 9 tasks
- Shared (Foundation, Testing): 47 tasks

**Estimated Effort**: ~120 hours (5 weeks × 24 hours/week)

---

## Next Steps

1. **Begin Phase 1**: Start with T001 (create enums)
2. **Sequential Implementation**: Complete foundation before user stories
3. **Test Continuously**: Write tests alongside implementation
4. **Commit Frequently**: Commit after each completed task or logical unit
5. **Update Task Status**: Mark tasks complete as you progress

**Ready to start**: ✅ Yes - begin with T001
