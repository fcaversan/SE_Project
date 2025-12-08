# Vehicle Connect - Home Screen & Vehicle Status

A web-based vehicle status dashboard built with Flask and vanilla JavaScript.

**Status**: ✅ **Prototype Complete** - All 5 user stories implemented with 94% test coverage

## Features

- **Battery Status Display** (P1 - MVP): View battery percentage, range estimate, and visual indicators ✅
- **Security Status** (P1): Monitor vehicle lock status with security warnings ✅
- **Climate Control** (P2): Check cabin temperature and HVAC status ✅
- **Vehicle Visualization** (P3): Graphical vehicle representation ✅
- **Pull-to-Refresh** (P2): Manual and automatic data refresh ✅

**Additional Features**:
- User preferences for distance units (km/mi) and temperature (°C/°F)
- Error handling with cached data fallback
- Stale data indicators (>60 seconds)
- Low/critical battery warnings
- Unlocked security warnings (>10 minutes)
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
├── app.py                  # Main Flask application
├── models/                 # Data models
├── services/               # Business logic services
├── presenters/             # Presentation layer
├── mocks/                  # Mock data and services
├── static/                 # Frontend assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Images and graphics
├── templates/              # HTML templates
├── data/                   # JSON data files
└── tests/                  # Test suite
    ├── unit/              # Unit tests
    └── integration/       # Integration tests
```

## Development Guidelines

See `.specify/memory/constitution.md` for the project's core development principles.

## Quality Metrics

- **Test Coverage**: 94% (target: ≥85%) ✅
- **Tests**: 56 tests (all passing) ✅
- **Flake8**: 0 critical errors ✅
- **Constitution Compliance**: 8/8 principles ✅

## Demo

See `DEMO.md` for comprehensive feature demonstration guide.

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
