# Tasks: Home Screen & Vehicle Status Display

**Input**: Design documents from `/specs/001-home-screen-vehicle-status/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅

**Organization**: Tasks are grouped by user story (US1-US5) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- File paths reference repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directory structure: `app.py`, `models/`, `services/`, `presenters/`, `mocks/`, `static/css/`, `static/js/`, `static/images/`, `templates/`, `data/`, `tests/`
- [ ] T002 Initialize Python project with requirements.txt (Flask>=3.0, pytest>=7.4, pytest-flask, flake8, pylint)
- [ ] T003 [P] Configure pytest with pytest.ini (test paths, coverage settings)
- [ ] T004 [P] Configure flake8 with .flake8 file (line length 100, exclude venv)
- [ ] T005 [P] Create .gitignore for data/ directory and __pycache__
- [ ] T006 [P] Create README.md with setup instructions and quick start commands

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create enums in `models/enums.py` (UnitSystem, TempUnit, LockStatus) per UML class diagram
- [ ] T008 Create VehicleState model in `models/vehicle_state.py` with all attributes per UML class diagram
- [ ] T009 Create UserProfile model in `models/user_profile.py` per UML class diagram
- [ ] T010 Create data persistence utilities in `services/data_persistence.py` (atomic write, safe read with file locking)
- [ ] T011 Create VehicleDataService interface in `services/vehicle_data_service.py` per UML class diagram
- [ ] T012 Create mock data scenarios in `mocks/mock_responses.py` (normal, low battery, unlocked, offline)
- [ ] T013 Implement VehicleDataMockService in `mocks/vehicle_data_mock.py` with configurable delays and failures
- [ ] T014 Create HomeScreenPresenter in `presenters/home_screen_presenter.py` per UML class diagram (format methods, unit conversions)
- [ ] T015 Create base Flask app in `app.py` with basic route structure and error handlers
- [ ] T016 [P] Create base HTML template in `templates/base.html` with common layout and meta tags
- [ ] T017 [P] Create CSS variables in `static/css/variables.css` (colors, spacing, light/dark themes)
- [ ] T018 [P] Create layout CSS in `static/css/layout.css` (grid structure, mobile-first responsive)
- [ ] T019 [P] Create utility functions in `static/js/utils.js` (debounce, formatTimestamp, etc.)
- [ ] T020 [P] Create API client in `static/js/api-client.js` (fetch wrapper, error handling)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Battery Status and Range (Priority: P1) 🎯 MVP

**Goal**: Display battery SoC percentage, visual indicator, and estimated range with user's preferred units

**Independent Test**: Open app and verify battery percentage (e.g., "82%"), battery icon/progress bar, and range display (e.g., "350 km"). Low battery scenarios show warning state. Stale data shows "last updated" timestamp.

### Implementation for User Story 1

- [ ] T021 [P] [US1] Implement range calculation algorithm in `services/range_calculator.py` per research.md (SoC, temp adjustment)
- [ ] T022 [P] [US1] Add unit conversion methods to HomeScreenPresenter in `presenters/home_screen_presenter.py` (km↔mi)
- [ ] T023 [US1] Create Flask route GET `/api/vehicle/status` in `app.py` returning VehicleState as JSON
- [ ] T024 [US1] Create Flask route GET `/` serving home screen template in `app.py`
- [ ] T025 [P] [US1] Create home screen HTML in `templates/home.html` with battery section structure
- [ ] T026 [P] [US1] Create battery component CSS in `static/css/components.css` (percentage display, progress bar, warning states)
- [ ] T027 [US1] Implement battery display logic in `static/js/home-screen.js` (update SoC, range, visual indicator)
- [ ] T028 [US1] Implement low battery warning logic in `static/js/home-screen.js` (SoC < 20% amber, < 5% red)
- [ ] T029 [US1] Implement stale data indicator in `static/js/home-screen.js` ("last updated" timestamp, highlight if > 60s)
- [ ] T030 [US1] Add initial data load on page load in `static/js/home-screen.js`

**Checkpoint**: User Story 1 complete - battery status and range displayable with mock data

---

## Phase 4: User Story 2 - Monitor Vehicle Security Status (Priority: P1)

**Goal**: Display vehicle lock status (Locked/Unlocked) with clear indicators and security warnings for prolonged unlocked state

**Independent Test**: View lock status indicator showing "Locked" or "Unlocked" with appropriate icon. If unlocked > 10 minutes, warning (amber) appears.

### Implementation for User Story 2

- [ ] T031 [P] [US2] Add lock status section to `templates/home.html` with icon and text placeholders
- [ ] T032 [P] [US2] Create lock status styles in `static/css/components.css` (locked/unlocked icons, amber warning)
- [ ] T033 [US2] Implement lock status display in `static/js/home-screen.js` (read lockStatus from API, update UI)
- [ ] T034 [US2] Implement unlocked warning logic in `static/js/home-screen.js` (check if unlocked > 10 min, show amber indicator)
- [ ] T035 [US2] Update mock data in `mocks/mock_responses.py` to include unlocked scenario with timestamp

**Checkpoint**: User Story 2 complete - lock status displayable with warnings

---

## Phase 5: User Story 3 - Check Climate Control Status (Priority: P2)

**Goal**: Display cabin temperature in user's preferred units and indicate whether climate control (HVAC) is active

**Independent Test**: View cabin temperature (e.g., "22°C" or "72°F") and climate status ("Climate On" or "Climate Off"). Active climate shows animation/icon.

### Implementation for User Story 3

- [ ] T036 [P] [US3] Add temperature conversion methods to HomeScreenPresenter in `presenters/home_screen_presenter.py` (°C↔°F)
- [ ] T037 [P] [US3] Add climate section to `templates/home.html` with temperature and status placeholders
- [ ] T038 [P] [US3] Create climate styles in `static/css/components.css` (temperature display, active/inactive indicators, animation)
- [ ] T039 [US3] Implement climate display in `static/js/home-screen.js` (temperature, HVAC status, animation)
- [ ] T040 [US3] Update mock data in `mocks/mock_responses.py` to include climate active/inactive scenarios

**Checkpoint**: User Story 3 complete - climate status displayable

---

## Phase 6: User Story 4 - View Vehicle Visualization (Priority: P3)

**Goal**: Display graphical representation of the vehicle on home screen for visual engagement

**Independent Test**: Vehicle image/graphic displays correctly, scales for different screen sizes without obscuring data.

### Implementation for User Story 4

- [ ] T041 [P] [US4] Add placeholder vehicle SVG image to `static/images/vehicle-placeholder.svg`
- [ ] T042 [P] [US4] Add vehicle visualization section to `templates/home.html`
- [ ] T043 [P] [US4] Create vehicle visualization styles in `static/css/home-screen.css` (responsive sizing, positioning)
- [ ] T044 [US4] Implement vehicle image display in `static/js/home-screen.js` (load image, handle missing images)

**Checkpoint**: User Story 4 complete - vehicle visualization displayable

---

## Phase 7: User Story 5 - Pull-to-Refresh Vehicle Data (Priority: P2)

**Goal**: Enable manual data refresh via pull-to-refresh gesture and implement auto-refresh every 60 seconds

**Independent Test**: Pull down on screen triggers loading indicator and fetches fresh data. Data auto-refreshes every 60 seconds while page active.

### Implementation for User Story 5

- [ ] T045 [P] [US5] Create refresh indicator HTML in `templates/home.html` (loading spinner)
- [ ] T046 [P] [US5] Create refresh indicator styles in `static/css/components.css` (spinner animation)
- [ ] T047 [US5] Implement pull-to-refresh gesture in `static/js/home-screen.js` (touchstart, touchmove, touchend events)
- [ ] T048 [US5] Implement manual refresh function in `static/js/home-screen.js` (call API, update UI, show loading)
- [ ] T049 [US5] Implement auto-refresh timer in `static/js/home-screen.js` (setInterval 60s, Page Visibility API)
- [ ] T050 [US5] Implement debounce for rapid refreshes in `static/js/home-screen.js` (min 3s between refreshes)
- [ ] T051 [US5] Add error handling for failed refresh in `static/js/home-screen.js` (show error, keep cached data)

**Checkpoint**: User Story 5 complete - refresh mechanisms functional

---

## Phase 8: User Preferences & Settings

**Purpose**: Enable users to configure distance and temperature units

- [ ] T052 [P] Create settings page template in `templates/settings.html` with unit preference forms
- [ ] T053 [P] Create settings page styles in `static/css/components.css` (form layout, radio buttons)
- [ ] T054 Create Flask routes in `app.py`: GET `/api/user/profile` and PUT `/api/user/profile`
- [ ] T055 Implement settings page logic in `static/js/settings.js` (load preferences, save on change)
- [ ] T056 Update home screen to load user preferences on init in `static/js/home-screen.js`
- [ ] T057 Update HomeScreenPresenter to use user preferences for conversions in `presenters/home_screen_presenter.py`

**Checkpoint**: User preferences functional

---

## Phase 9: Error Handling & Edge Cases

**Purpose**: Handle offline mode, stale data, network errors gracefully

- [ ] T058 [P] Create error message component in `templates/home.html` (banner for errors)
- [ ] T059 [P] Create error styles in `static/css/components.css` (error banner, warning colors)
- [ ] T060 Implement offline detection in `static/js/home-screen.js` (catch fetch errors, show cached data)
- [ ] T061 Implement network error handling in `static/js/api-client.js` (timeout handling, retry logic)
- [ ] T062 Add "Unable to reach vehicle" message display in `static/js/home-screen.js`
- [ ] T063 Implement critical battery warning (SoC < 5%) in `static/js/home-screen.js` (banner: "Charge immediately")
- [ ] T064 Update mock service in `mocks/vehicle_data_mock.py` to simulate offline/error scenarios

**Checkpoint**: Error scenarios handled gracefully

---

## Phase 10: Testing & Quality

**Purpose**: Achieve ≥85% test coverage and verify all acceptance criteria

- [ ] T065 [P] Write unit tests for range calculation in `tests/unit/test_range_calculator.py`
- [ ] T066 [P] Write unit tests for unit conversions in `tests/unit/test_unit_conversions.py`
- [ ] T067 [P] Write unit tests for VehicleState model in `tests/unit/test_vehicle_state.py`
- [ ] T068 [P] Write unit tests for HomeScreenPresenter in `tests/unit/test_home_screen_presenter.py`
- [ ] T069 Write integration test for vehicle data flow in `tests/integration/test_vehicle_data_flow.py`
- [ ] T070 Write integration test for cache persistence in `tests/integration/test_cache_persistence.py`
- [ ] T071 Write integration test for mock API in `tests/integration/test_mock_api.py`
- [ ] T072 Run pytest with coverage report, verify ≥85% coverage
- [ ] T073 Run flake8 linter, fix all violations to achieve score ≥8.0/10
- [ ] T074 Validate HTML with W3C validator, fix semantic errors
- [ ] T075 Test UI in Chrome, Firefox, Safari, Edge - verify responsive layout
- [ ] T076 Test all 5 user story acceptance scenarios with mock data
- [ ] T077 Verify UML compliance: compare Python classes to `docs/uml/class/Home_Screen_Vehicle_Status_v3_class_diagram.puml`

**Checkpoint**: All tests passing, quality gates met

---

## Phase 11: Polish & Documentation

**Purpose**: Final touches for demo readiness

- [ ] T078 [P] Add loading skeleton UI for initial page load in `templates/home.html` and CSS
- [ ] T079 [P] Add smooth transitions/animations in `static/css/components.css` (fade-in, slide)
- [ ] T080 [P] Optimize CSS (remove unused styles, organize logically)
- [ ] T081 [P] Add code comments and docstrings where missing
- [ ] T082 [P] Update README.md with demo instructions and feature screenshots
- [ ] T083 Create demo script showing all 5 user stories
- [ ] T084 Test demo flow end-to-end, verify all features work
- [ ] T085 Create data/vehicle_state.json with realistic initial mock data
- [ ] T086 Create data/user_settings.json with default METRIC units

**Checkpoint**: Demo ready

---

## Dependencies & Execution Order

### Critical Path (Must Be Sequential)
1. **Phase 1** (Setup) → **Phase 2** (Foundation) → All user stories can proceed in parallel
2. Within each user story: Implementation tasks are mostly sequential but CSS/HTML can be parallel

### Parallelization Opportunities

**After Phase 2 completes, these can run in parallel:**
- **Track A**: User Story 1 (T021-T030) - Battery display
- **Track B**: User Story 2 (T031-T035) - Lock status  
- **Track C**: User Story 3 (T036-T040) - Climate status
- **Track D**: User Story 4 (T041-T044) - Vehicle viz
- **Track E**: User Story 5 (T045-T051) - Refresh

**Test tasks (Phase 10) can mostly run in parallel** (T065-T071)

**Polish tasks (Phase 11) can mostly run in parallel** (T078-T082)

---

## MVP Strategy (Minimum Viable Product)

**MVP = User Story 1 Only** (T001-T030)

This delivers immediate value:
✅ Battery percentage display  
✅ Estimated range display  
✅ Visual battery indicator  
✅ Low battery warnings  
✅ Stale data indicators

**Demo-able with just MVP**: User can open app and see vehicle's charge status and range - core value proposition complete.

---

## Incremental Delivery Plan

**Sprint 1 (Week 1)**: MVP - User Story 1 (T001-T030)  
**Sprint 2 (Week 2)**: Add User Story 2 (Lock Status) + User Story 5 (Refresh) (T031-T051)  
**Sprint 3 (Week 3)**: Add User Story 3 (Climate) + User Story 4 (Vehicle Viz) + Settings (T036-T057)  
**Sprint 4 (Week 4)**: Error Handling (T058-T064)  
**Sprint 5 (Week 5)**: Testing & Polish (T065-T086)

Each sprint delivers a demo-able increment.

---

## Task Summary

**Total Tasks**: 86  
**Setup/Foundation**: 20 tasks (T001-T020)  
**User Story 1** (P1 - MVP): 10 tasks (T021-T030)  
**User Story 2** (P1): 5 tasks (T031-T035)  
**User Story 3** (P2): 5 tasks (T036-T040)  
**User Story 4** (P3): 4 tasks (T041-T044)  
**User Story 5** (P2): 7 tasks (T045-T051)  
**User Preferences**: 6 tasks (T052-T057)  
**Error Handling**: 7 tasks (T058-T064)  
**Testing**: 13 tasks (T065-T077)  
**Polish**: 9 tasks (T078-T086)

**Parallel Opportunities**: 29 tasks marked with [P]  
**Independent Stories**: All 5 user stories can be developed/tested independently after Phase 2

---

**Next Step**: Run `/speckit.implement` to begin implementation following this task breakdown.
