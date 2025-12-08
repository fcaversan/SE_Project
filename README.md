# Vehicle Connect - EV Companion App

A web-based vehicle management dashboard built with Flask and vanilla JavaScript, providing comprehensive vehicle monitoring and remote control capabilities.

**Status**: ✅ **Phase 1 Complete** (Home Screen) | 🚀 **Phase 2 In Progress** (Remote Controls)

## Features

### Home Screen (Phase 1) ✅
- **Battery Status Display** (P1 - MVP): View battery percentage, range estimate, and visual indicators
- **Security Status** (P1): Monitor vehicle lock status with security warnings
- **Climate Control** (P2): Check cabin temperature and HVAC status
- **Vehicle Visualization** (P3): Graphical vehicle representation
- **Pull-to-Refresh** (P2): Manual and automatic data refresh

### Remote Controls (Phase 2) 🚀
- **Lock/Unlock** (US1): Remote vehicle locking and unlocking with optimistic UI
- **Climate Control** (US2-US4): 
  - Remote start/stop HVAC
  - Adjustable temperature (15-30°C)
  - Heated seats (4 levels: off, low, medium, high)
  - Heated steering wheel
  - Front/rear defrost with 15-min auto-shutoff
- **Trunk/Frunk Control** (US5): 
  - Open rear trunk remotely
  - Open front trunk (frunk) remotely
  - Safety checks (prevents opening while moving)
  - Cannot be closed remotely (safety feature)
- **Vehicle Locator** (US6):
  - Honk horn and flash lights
  - 10-second cooldown between activations

**Additional Features**:
- User preferences for distance units (km/mi) and temperature (°C/°F)
- Error handling with cached data fallback
- Stale data indicators (>60 seconds)
- Low/critical battery warnings
- Unlocked security warnings (>10 minutes)
- Command status polling with haptic feedback
- Mobile-first responsive design
- Dark mode support (system preference)

## Technology Stack

- **Backend**: Python 3.11+ with Flask
- **Frontend**: Vanilla HTML5, CSS3, JavaScript ES6+
- **Data**: JSON file persistence (no database)
- **Testing**: pytest with ≥85% coverage target

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

```powershell
# Clone the repository
git clone https://github.com/fcaversan/SE_Project.git
cd SE_Project

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```powershell
# Start the Flask development server
python app.py
```

Navigate to `http://localhost:5000` in your browser.

### Running Tests

```powershell
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_vehicle_state.py

# Run with verbose output
pytest -v
```

### Code Quality

```powershell
# Run flake8 linter
flake8 .

# Run pylint
pylint models services presenters mocks app.py
```

## Project Structure

```
SE_Project/
├── app.py                  # Main Flask application with API endpoints
├── models/                 # Data models
│   ├── vehicle_state.py   # Vehicle state with climate & trunk status
│   ├── climate_settings.py # Complete climate control state
│   ├── trunk_status.py    # Trunk/frunk status
│   ├── remote_command.py  # Remote command model
│   └── enums.py           # Command types, statuses, heat levels
├── services/               # Business logic services
│   ├── vehicle_data_service.py
│   ├── remote_command_service.py
│   └── data_persistence.py
├── mocks/                  # Mock data and services
│   ├── vehicle_data_mock.py
│   └── remote_command_mock.py
├── static/                 # Frontend assets
│   ├── css/               # Stylesheets (home.css, controls.css)
│   ├── js/                # JavaScript (home.js, controls.js)
│   └── images/            # Images and graphics
├── templates/              # HTML templates
│   ├── home.html          # Home screen (Phase 1)
│   └── controls.html      # Remote controls (Phase 2)
├── data/                   # JSON data persistence
├── specs/                  # Feature specifications
│   ├── 001-home-screen/
│   └── 002-remote-controls/
└── tests/                  # Test suite
    ├── unit/              # 136 unit tests
    └── integration/       # 55 integration tests
```

## Development Guidelines

See `.specify/memory/constitution.md` for the project's core development principles.

## Quality Metrics

- **Test Coverage**: Target ≥85%
- **Tests**: 191 tests (136 unit + 55 integration) ✅
- **Phases Complete**: 2 of 2 (Home Screen ✅, Remote Controls 🚀)
- **Constitution Compliance**: 8/8 principles ✅

## Demo

See `DEMO.md` for comprehensive feature demonstration guide.

## Routes

### Home Screen
- `GET /` - Home screen dashboard

### Remote Controls  
- `GET /controls` - Remote controls page
- `POST /api/vehicle/lock` - Lock vehicle
- `POST /api/vehicle/unlock` - Unlock vehicle
- `POST /api/vehicle/climate` - Start/stop climate
- `PUT /api/vehicle/climate` - Set temperature
- `POST /api/vehicle/seat-heat` - Control heated seats
- `POST /api/vehicle/steering-heat` - Control heated steering
- `POST /api/vehicle/defrost` - Control defrost
- `POST /api/vehicle/trunk/open` - Open rear trunk
- `POST /api/vehicle/frunk/open` - Open front trunk
- `POST /api/vehicle/honk-flash` - Honk horn & flash lights
- `GET /api/vehicle/status` - Get vehicle state
- `GET /api/vehicle/command/{id}` - Poll command status

## Architecture

**Frontend**: Vanilla HTML5/CSS3/JavaScript ES6+
- Mobile-first responsive design (Grid + Flexbox)
- Page Visibility API for auto-refresh
- Touch events for pull-to-refresh

**Backend**: Python 3.11+ with Flask
- RESTful API design
- Mock service with configurable scenarios
- Atomic writes with file locking

**Data**: JSON file persistence
- `data/vehicle_state.json` - Cached vehicle data
- `data/user_settings.json` - User preferences

## License

Copyright © 2025. All rights reserved.
