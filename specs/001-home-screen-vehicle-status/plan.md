# Implementation Plan: Home Screen & Vehicle Status Display

**Branch**: `001-home-screen-vehicle-status` | **Date**: 2025-12-07 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `/specs/001-home-screen-vehicle-status/spec.md`

## Summary

Implement the home screen of the Vehicle Connect web application that displays real-time vehicle status information including battery State of Charge (SoC), estimated range, lock status, cabin temperature, and climate control status. The feature will use a Python backend (Flask) with vanilla HTML/CSS/JavaScript frontend, mock vehicle data APIs, and JSON file-based persistence. All implementation must comply with UML diagrams in `docs/uml/` directory.

**Primary Requirements**:
- Display battery SoC (%) and estimated range with visual indicators
- Show vehicle lock status (Locked/Unlocked) with security warnings
- Display cabin temperature and climate control status
- Support user preferences for units (METRIC/IMPERIAL, °C/°F)
- Implement pull-to-refresh for manual data updates
- Handle offline scenarios with cached data and staleness indicators

**Technical Approach**:
- Python 3.11+ with Flask for web server and API endpoints
- Vanilla HTML5, CSS3 (Flexbox/Grid), JavaScript (ES6+) for frontend
- Mock vehicle data service simulating TCU responses with realistic delays
- JSON files for data persistence (vehicle_state.json, user_settings.json)
- UML-driven development following class, activity, and sequence diagrams

## Technical Context

**Language/Version**: Python 3.11+ (backend), ES6+ JavaScript (frontend)  
**Primary Dependencies**: 
- Backend: Flask 3.0+ (web framework), pytest (testing)
- Frontend: None (vanilla JavaScript, no frameworks)

**Storage**: JSON files in `/data/` directory (vehicle_state.json, user_settings.json)  
**Testing**: 
- Backend: pytest with pytest-flask for unit and integration tests
- Frontend: Browser console testing, manual UI testing
- Linting: pylint/flake8 (Python), basic JavaScript console validation

**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions), Python 3.11+ runtime  
**Project Type**: Web application (frontend + backend)  
**Performance Goals**: 
- 4-second cold start to usable home screen
- 3-second max response time for data refresh
- 60-second automatic data refresh interval
- Smooth UI interactions (<100ms response to user input)

**Constraints**: 
- No database systems (SQLite, PostgreSQL, etc.) - JSON files only
- No complex frontend frameworks (React, Vue, Angular)
- No real vehicle integration - all data mocked
- No production security (basic auth only, no TLS/encryption)
- Prototype-focused: demonstration over production robustness

**Scale/Scope**: 
- Single user prototype (no multi-user concerns)
- ~8 Python classes following UML class diagram
- ~5 HTML templates (home screen, settings, error pages)
- ~500-800 lines of Python code
- ~400-600 lines of JavaScript code
- ~300-500 lines of CSS

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Security-First Development
**Status**: DEFERRED (documented)  
**Compliance**: Basic authentication only for prototype. Production security (biometrics, TLS, certificate pinning) explicitly deferred per Constitution Principle VII (Prototype-First Development). Mock data has no real security risks.

### ✅ II. Performance Excellence
**Status**: COMPLIANT  
**Compliance**: Requirements specify 3-second response times, 4-second cold start, 60-second data freshness matching constitution performance standards. Mocked delays will demonstrate these behaviors.

### ✅ III. User-Centric Design  
**Status**: COMPLIANT  
**Compliance**: Specification includes 5 prioritized user stories with acceptance criteria. Primary functions (battery, lock status) accessible with minimal interaction. Pull-to-refresh gesture included. Error messages defined as user-friendly.

### ✅ IV. Test-Driven Development
**Status**: COMPLIANT  
**Compliance**: Success criteria #13 requires unit tests for range calculation, data formatting, state management. Integration tests for data retrieval. Acceptance scenarios defined for each user story provide test cases.

### ✅ V. Web-Based Simplicity
**Status**: COMPLIANT  
**Compliance**: Python backend with Flask. Vanilla HTML/CSS/JavaScript frontend (no frameworks). Specification explicitly avoids complex build tools and frameworks.

### ✅ VI. Mock-First Integration
**Status**: COMPLIANT  
**Compliance**: All vehicle API calls will be mocked per specification assumptions. Mock responses include realistic delays (1-3 seconds). Clear separation between mock layer and application logic planned in architecture.

### ✅ VII. Prototype-First Development
**Status**: COMPLIANT  
**Compliance**: Specification explicitly states this is demonstration prototype. JSON file persistence instead of database. Production security deferred. Focus on demonstration value.

### ✅ VIII. Design-Driven Implementation
**Status**: COMPLIANT  
**Compliance**: Specification references UML diagrams in `docs/uml/` throughout. Success criteria #11 requires UML compliance. Technical Notes section describes class structure matching UML.

**Overall Assessment**: ✅ ALL GATES PASSED - No violations, proceed to implementation.

## Project Structure

### Documentation (this feature)

```text
specs/001-home-screen-vehicle-status/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (IN PROGRESS)
├── research.md          # Phase 0 output (TO BE CREATED)
├── data-model.md        # Phase 1 output (TO BE CREATED)
├── quickstart.md        # Phase 1 output (TO BE CREATED)
├── contracts/           # Phase 1 output (TO BE CREATED)
│   └── vehicle_api.yaml # OpenAPI spec for mock vehicle API
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
# Web application structure (Python backend + HTML/CSS/JS frontend)

# Backend
app.py                      # Main Flask application entry point
mocks/
├── __init__.py
├── vehicle_data_mock.py    # Mock VehicleDataService implementation
└── mock_responses.py       # Predefined mock data scenarios

models/
├── __init__.py
├── vehicle_state.py        # VehicleState class (UML: VehicleState)
├── user_profile.py         # UserProfile class (UML: UserProfile)
└── enums.py                # UnitSystem, TempUnit, LockStatus enums (UML)

services/
├── __init__.py
├── vehicle_data_service.py # VehicleDataService interface (UML)
├── data_persistence.py     # JSON file read/write utilities
└── range_calculator.py     # Range estimation algorithm (FR-HSS-004)

presenters/
├── __init__.py
└── home_screen_presenter.py # HomeScreenPresenter (UML)

# Frontend
static/
├── css/
│   ├── variables.css       # CSS custom properties (colors, spacing)
│   ├── layout.css          # Flexbox/Grid layout styles
│   ├── components.css      # Reusable UI component styles
│   └── home-screen.css     # Home screen specific styles
├── js/
│   ├── api-client.js       # Fetch wrapper for backend API calls
│   ├── home-screen.js      # Home screen UI logic and data binding
│   ├── unit-converter.js   # Frontend unit conversion utilities
│   └── utils.js            # Common utilities (debounce, formatters)
└── images/
    └── vehicle-placeholder.svg # Default vehicle visualization

templates/
├── base.html               # Base template with common layout
├── home.html               # Home screen template
├── settings.html           # User settings page (future)
└── error.html              # Error page template

# Data storage
data/
├── vehicle_state.json      # Cached vehicle status data
├── user_settings.json      # User preferences (units)
└── .gitignore              # Exclude data files from Git

# Tests
tests/
├── __init__.py
├── unit/
│   ├── test_vehicle_state.py       # VehicleState model tests
│   ├── test_range_calculator.py    # Range calculation logic tests
│   ├── test_home_screen_presenter.py # Data formatting tests
│   └── test_unit_conversions.py    # Unit conversion tests
├── integration/
│   ├── test_vehicle_data_flow.py   # End-to-end data retrieval
│   ├── test_cache_persistence.py   # JSON file operations
│   └── test_mock_api.py            # Mock service integration
└── fixtures/
    └── mock_data.json              # Test data fixtures

# Configuration
requirements.txt            # Python dependencies
pytest.ini                 # Pytest configuration
.flake8                    # Flake8 linter configuration
```

**Structure Decision**: Selected Web application structure (backend + frontend) as this is a web-based prototype using Python Flask backend and vanilla HTML/CSS/JS frontend. Structure follows constitutional standards for organization (Technology Standards section) and supports clear separation between presentation, application, service, and data layers as defined in UML architecture.

## Complexity Tracking

> **No violations to justify - all Constitution gates passed**

---

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Flask Application Structure for Simple Web Apps**
   - Best practices for Flask project organization
   - Recommended patterns for serving HTML templates + JSON API
   - Session management for user preferences

2. **Mock Data Patterns in Python**
   - Strategies for simulating async delays (realistic 1-3 second responses)
   - Mock data state management (changing vehicle state over time)
   - Error scenario simulation (network failures, stale data)

3. **JSON File Persistence Best Practices**
   - Thread-safe file read/write in Flask
   - Atomic write operations to prevent corruption
   - File locking strategies for concurrent access

4. **Frontend Data Binding Without Frameworks**
   - Vanilla JavaScript patterns for updating DOM efficiently
   - Pull-to-refresh implementation (touch events, visual feedback)
   - Polling strategies for auto-refresh (setInterval with visibility API)

5. **Range Calculation Algorithms for EVs**
   - Industry-standard formulas for EV range estimation
   - Temperature impact factors on battery performance
   - Energy consumption trend averaging methods

6. **CSS Responsive Design Patterns**
   - Mobile-first design approach with Flexbox/Grid
   - CSS custom properties for theming (light/dark mode)
   - Accessible visual indicators for warnings/statuses

### Research Outputs

See `research.md` for detailed findings and decisions.

---

## Phase 1: Design & Contracts

### Data Model

See `data-model.md` for complete entity definitions, relationships, and validation rules.

**Key Entities**:
- `VehicleState`: Current vehicle status data (SoC, range, lock status, temperature)
- `UserProfile`: User preferences (distance/temperature units)
- `VehicleVisualization`: Vehicle image/model metadata
- Enums: `UnitSystem`, `TempUnit`, `LockStatus`

### API Contracts

See `contracts/vehicle_api.yaml` for OpenAPI specification.

**Key Endpoints**:
- `GET /api/vehicle/status` - Retrieve current vehicle status
- `POST /api/vehicle/refresh` - Trigger manual data refresh
- `GET /api/user/profile` - Get user preferences
- `PUT /api/user/profile` - Update user preferences

### Quickstart Guide

See `quickstart.md` for development setup and running instructions.

**Quick Commands**:
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python app.py

# Run tests
pytest

# Access application
http://localhost:5000
```

---

## Phase 2: Task Breakdown

To be generated via `/speckit.tasks` command.

---

## Implementation Milestones

### Milestone 1: Foundation (Week 1)
**Goal**: Basic Flask app serving home screen with static mock data

**Deliverables**:
- Flask application structure created
- HTML/CSS home screen template with placeholder data
- Mock data service with hardcoded VehicleState
- Basic pytest configuration

**Success Criteria**:
- App launches and serves home screen at localhost:5000
- Static battery percentage, range, lock status displayed
- Page renders correctly in Chrome, Firefox, Safari

### Milestone 2: Data Flow (Week 2)  
**Goal**: Dynamic data retrieval and display with JSON persistence

**Deliverables**:
- VehicleDataService implementation with mock delays
- JSON file read/write utilities
- JavaScript API client for fetching data
- Range calculation algorithm
- Unit conversion logic (METRIC/IMPERIAL)

**Success Criteria**:
- Home screen displays data fetched from backend API
- Data persists to vehicle_state.json and reloads on refresh
- User can switch between units and see converted values
- Range calculation works correctly with SoC and temperature

### Milestone 3: User Interactions (Week 3)
**Goal**: Pull-to-refresh, auto-refresh, and user preferences

**Deliverables**:
- Pull-to-refresh gesture implementation
- Auto-refresh timer (60-second interval)
- User settings page for unit preferences
- "Last updated" timestamp display
- Loading states and spinners

**Success Criteria**:
- Pull-to-refresh triggers data fetch with visual feedback
- Data auto-refreshes every 60 seconds when screen active
- User preferences save to JSON and persist across sessions
- Loading states display during data fetching

### Milestone 4: Error Handling & Edge Cases (Week 4)
**Goal**: Offline mode, stale data handling, warnings

**Deliverables**:
- Offline mode detection and cached data display
- Staleness indicators for old data
- Low battery warnings (SoC < 20%, < 5%)
- Unlocked vehicle warning (> 10 minutes)
- Error messages for failed requests

**Success Criteria**:
- App displays cached data when mock service unavailable
- "Last updated" timestamp shows and highlights stale data
- Battery warnings appear at correct thresholds
- Network errors show user-friendly messages

### Milestone 5: Polish & Testing (Week 5)
**Goal**: Complete test coverage, UML compliance verification, demo readiness

**Deliverables**:
- Full unit test suite (≥85% coverage)
- Integration tests for all user stories
- UML compliance validation (classes match diagrams)
- Browser compatibility testing
- Code linting and cleanup

**Success Criteria**:
- All acceptance scenarios pass
- Test coverage ≥85%
- Linting scores ≥8.0/10
- Demo can show all 5 user stories
- All success criteria from spec.md verified

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| JSON file corruption during concurrent writes | Medium | High | Implement atomic writes with temp files, add file locking |
| Pull-to-refresh not working on all browsers | Low | Medium | Use standard touch events, test on all target browsers |
| Auto-refresh consuming excessive resources | Low | Low | Use Visibility API to pause when page hidden |
| Range calculation inaccuracy | Medium | Low | Use simplified but documented algorithm, mark as prototype |
| CSS layout breaking on small screens | Medium | Medium | Mobile-first approach, test on various viewport sizes |

### Project Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep from SRS requirements | Medium | High | Strict "Out of Scope" section, focus only on FR-HSS requirements |
| UML diagrams not matching implementation needs | Low | Medium | Review UML early, update diagrams before code if needed |
| Insufficient time for test coverage | Medium | Medium | Write tests alongside code (TDD), prioritize critical paths |
| Browser compatibility issues discovered late | Low | Medium | Test in all browsers from Milestone 1 |

---

## Dependencies

### External Dependencies
- Python 3.11+ runtime
- Flask web framework
- Modern web browsers (Chrome 120+, Firefox 121+, Safari 17+, Edge 120+)

### Internal Dependencies
- UML diagrams in `docs/uml/` (class, activity, sequence) - COMPLETE ✅
- Constitution document (`.specify/memory/constitution.md`) - COMPLETE ✅
- SRS document (`docs/SRS.md`) - COMPLETE ✅

### Blocking Dependencies
- None - all prerequisites complete, can proceed to implementation

---

## Next Steps

1. ✅ **Specification Complete** - `specs/001-home-screen-vehicle-status/spec.md`
2. ✅ **Implementation Plan Complete** - This document
3. ⏭️ **Generate Research** - Run Phase 0 to create `research.md`
4. ⏭️ **Generate Data Model** - Run Phase 1 to create `data-model.md`
5. ⏭️ **Generate API Contracts** - Run Phase 1 to create `contracts/vehicle_api.yaml`
6. ⏭️ **Generate Quickstart** - Run Phase 1 to create `quickstart.md`
7. ⏭️ **Break Into Tasks** - Run `/speckit.tasks` to generate actionable task list
8. ⏭️ **Begin Implementation** - Run `/speckit.implement` to start coding

**Ready for**: `/speckit.tasks` to break this plan into actionable development tasks.
