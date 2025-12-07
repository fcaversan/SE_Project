<!--
Sync Impact Report:
- Version change: 1.1.0 → 1.2.0
- MINOR version bump: Added new principle (Design-Driven Implementation) requiring adherence to UML diagrams
- Modified sections: Added UML documentation requirement to Technology Standards and Quality Gates
- Templates status: ✅ All templates aligned with updated constitution
- Follow-up: UML diagrams should be added to /docs/uml/ directory
-->

# Vehicle Connect Mobile Application Constitution

## Core Principles

### I. Security-First Development (NON-NEGOTIABLE)

All features MUST prioritize security at every layer:
- User authentication MUST be required via biometrics (Face ID/fingerprint) or PIN before app access
- All API communication MUST use TLS 1.2 or higher with certificate pinning to prevent MITM attacks
- Sensitive data (tokens, credentials) MUST be encrypted when stored locally
- All vehicle commands MUST be authenticated and authorized before execution
- Phone as a Key (PaaK) implementation MUST use secure BLE/UWB protocols with encryption
- Compliance with GDPR, CCPA, and all relevant data privacy regulations is MANDATORY
- Security vulnerabilities MUST be addressed within 24 hours of discovery (critical) or 7 days (high severity)

**Rationale**: Given the safety-critical nature of remote vehicle control, security breaches could lead to physical harm, theft, or privacy violations. Security is non-negotiable.

### II. Performance Excellence

The application MUST deliver responsive, real-time experiences:
- Remote commands (lock, climate, etc.) MUST receive confirmation within 3 seconds under normal network conditions
- Vehicle status data MUST be no older than 60 seconds from last poll
- Cold app launch MUST reach usable home screen within 4 seconds
- UI interactions MUST feel instantaneous (<100ms response to touch)
- Offline mode MUST be graceful with cached data and clear "last updated" timestamps
- Battery consumption MUST be optimized; background updates MUST use efficient polling strategies

**Rationale**: Users expect instant control of their vehicle. Delays create frustration and erode trust in the system.

### III. User-Centric Design

Every feature MUST prioritize intuitive, accessible user experience:
- Primary functions (lock/unlock, climate, charge status) MUST be accessible from main screen with ≤1 tap
- UI MUST adhere to platform-specific guidelines (iOS Human Interface Guidelines, Android Material Design)
- Application MUST support both light and dark modes
- Application MUST be responsive across all supported device sizes
- Error messages MUST be clear, actionable, and user-friendly (no technical jargon)
- Haptic feedback MUST confirm critical actions (lock/unlock completion)
- Accessibility features MUST be implemented (VoiceOver, TalkBack, dynamic text sizing)

**Rationale**: Vehicle owners are not expected to have technical expertise. The interface must be self-explanatory and efficient for daily use.

### IV. Test-Driven Development (NON-NEGOTIABLE)

All code MUST follow rigorous testing practices:
- Unit tests MUST be written before implementation (Red-Green-Refactor)
- Code coverage MUST be ≥85% for all business logic and critical paths
- Integration tests MUST verify API communication, authentication flows, and vehicle command execution
- UI tests MUST cover primary user journeys (launch → lock, launch → charge control, etc.)
- Security tests MUST validate authentication, encryption, and certificate pinning
- Performance tests MUST verify response times for all requirements (NFR-PERF)
- All tests MUST pass before code can be merged to main branch

**Rationale**: Given the safety and security implications, bugs in production are unacceptable. Testing ensures reliability and maintains user trust.
### V. Web-Based Simplicity

The application MUST use straightforward, maintainable web technologies:
- MUST be developed using Python for all backend logic and server components
- MUST use vanilla HTML, CSS, and JavaScript for the frontend (no complex frameworks)
- UI MUST be clean, functional, and responsive without unnecessary complexity
- JavaScript MUST be minimal and focused on interactivity only
- CSS MUST follow modern best practices (Flexbox/Grid for layout, CSS variables for theming)
- Application MUST be accessible via standard web browsers (Chrome, Firefox, Safari, Edge)

**Rationale**: Web technologies provide rapid development, easy demonstration, and broad accessibility. Simplicity ensures maintainability and reduces learning curve for contributors.

### VI. Mock-First Integration

All backend interactions MUST be mocked for demonstration and development:
- All vehicle API calls MUST be emulated with realistic mock data and responses
- Mock responses MUST simulate realistic delays (1-3 seconds) to demonstrate async behavior
- API contracts MUST be documented for future real integration
- Mock data MUST be comprehensive enough to demonstrate all features
- Clear separation MUST exist between mock layer and application logic for future real API integration
- Mock implementations MUST include both success and error scenarios

**Rationale**: Without access to real vehicle systems or backend servers, mocking enables complete feature demonstration and development. Clear abstraction ensures easy transition to real APIs later.

### VII. Prototype-First Development

This is a demonstration prototype, NOT production software:
- Focus is on demonstrating functionality and user experience, not production robustness
- Database complexity is OUT OF SCOPE - use simple file-based persistence (JSON files)
- Real-time vehicle communication is OUT OF SCOPE - use mocked telemetry
- Production-grade security (encryption, auth) is DEFERRED - implement basic authentication only
- Deployment and scalability considerations are OUT OF SCOPE
- Code MUST be structured to allow future production hardening

**Rationale**: Prototype development prioritizes speed and demonstration value. Over-engineering at this stage wastes effort on requirements that may change.

- **API Mocking**: Python modules to simulate vehicle backend responses
- **Maps Integration**: Leaflet.js with OpenStreetMap (free, no API key)
- **Development Server**: Flask development server or Python's http.server
- **Version Control**: Git (already configured)
- **Design Documentation**: PlantUML (`.puml` files) stored in `/docs/uml/`
  - Class diagrams → `/docs/uml/class/`
  - Activity diagrams → `/docs/uml/activity/`
  - Sequence diagrams → `/docs/uml/sequence/`
  - PlantUML server or local renderer for viewing diagrams

### Prohibited Technologies (For This Phase)
- Mobile native frameworks (Swift, Kotlin, React Native, Flutter)
- Database systems (SQLite, PostgreSQL, MySQL, MongoDB)
- Complex frontend frameworks (React, Vue, Angular, Svelte)
- Build tools that add complexity (Webpack, Vite, etc.)
- Cloud services or external APIs requiring accounts/keys

### Code Quality Standardsllow the provided UML design diagrams:
- **Class Diagrams**: Define the structure of Python classes, attributes, methods, and relationships
- **Activity Diagrams**: Define workflows and business logic flow (e.g., charging workflow, authentication flow)
- **Sequence Diagrams**: Define interaction between components and timing of API calls
- UML diagrams are stored in PlantUML (`.puml`) format in `/docs/uml/` directory
- Implementation MUST NOT deviate from UML design without updating the diagrams first
- Class names, method signatures, and relationships MUST match the class diagrams
- Business logic flow MUST follow the activity diagrams
- Component interactions MUST follow the sequence diagrams
- Any proposed design changes MUST be reflected in updated UML diagrams before implementation
- Code reviews MUST verify compliance with UML diagrams

**Rationale**: UML diagrams provide the architectural blueprint. Following them ensures consistency, enables architectural review before coding, and maintains design documentation accuracy.

## Technology Standards

### Required Technology Stack (Prototype Phase)
- **Backend**: Python 3.11+ with Flask or FastAPI for web server
- **Frontend**: Vanilla HTML5, CSS3, and JavaScript (ES6+)
  - No frameworks (React, Vue, Angular) - keep it simple
  - Optional: Minimal libraries for specific needs (e.g., Leaflet for maps)
- **Persistence**: JSON files stored locally on the filesystem
  - Vehicle state data → `data/vehicle_state.json`
  - User settings → `data/user_settings.json`
  - Trip history → `data/trip_history.json`
  - No database system (SQLite, PostgreSQL, etc.) required
- **API Mocking**: Python modules to simulate vehicle backend responses
- **Maps Integration**: Leaflet.js with OpenStreetMap (free, no API key)
### Code Quality Standards
- Python code MUST follow PEP 8 style guidelines
- Python code MUST pass linting (pylint or flake8) with score ≥8.0/10
- HTML MUST be valid and semantic (use proper tags: `<nav>`, `<main>`, `<article>`, etc.)
- CSS MUST be organized logically (variables, layout, components, utilities)
- JavaScript MUST use modern ES6+ syntax (const/let, arrow functions, async/await)
- All functions MUST have docstrings (Python) or JSDoc comments (JavaScript)
- Complex business logic MUST include inline comments explaining "why" not "what"
- Magic numbers MUST be replaced with named constants
- Python classes and methods MUST match UML class diagram specifications
- File structure MUST be clear and organized:
  ```
  /static/       # CSS, JS, images
  /templates/    # HTML templates
  /data/         # JSON persistence files
  /mocks/        # Mock API implementations
  /docs/uml/     # PlantUML diagram files
  /app.py        # Main application entry
  ```

### Prohibited Technologies (For This Phase)
- Mobile native frameworks (Swift, Kotlin, React Native, Flutter)
- Database systems (SQLite, PostgreSQL, MySQL, MongoDB)
- Complex frontend frameworks (React, Vue, Angular, Svelte)
- Build tools that add complexity (Webpack, Vite, etc.)
- Cloud services or external APIs requiring accounts/keys

## Quality Gates

All releases MUST pass the following gates before deployment:

### Pre-Merge Gates
1. All automated tests pass (unit, integration, UI)
2. Code coverage ≥85%
3. No critical or high-severity security vulnerabilities
4. Code review approved by senior developer
5. Linter passes with score ≥8.0/10
6. **Implementation matches UML diagrams (class structure, method signatures, interactions)**

### Pre-Demo Gates (Adjusted for Prototype)
1. All functional requirements demonstrated (even if mocked)
2. Performance is acceptable for demonstration (no noticeable lag in UI)
3. Basic authentication implemented (simple login, no production security needed)
4. UI is clean, responsive, and works in modern browsers
5. Mock data is realistic and comprehensive
6. Demo script prepared showing key features

### Prototype Validation
- Application MUST run without crashes during demonstrations
- Mock API responses MUST be consistent and predictable
- File-based persistence MUST work reliably (read/write JSON files)
- UI MUST render correctly in Chrome, Firefox, Safari, and Edge
- Console errors MUST be addressed (no JavaScript errors in browser console)

## Development Workflow

### Feature Development Process
1. Requirements documented in SRS and approved by stakeholders
2. **UML diagrams reviewed and confirmed (class, activity, sequence as applicable)**
3. Technical design document created for complex features (if UML insufficient)
4. Tests written and approved (failing tests committed to feature branch)
5. Implementation following UML design specifications
6. Code review with at least one approval (including UML compliance check)
7. Merge to main after all gates pass
8. QA validation in staging environment
9. Production deployment with feature flags when appropriate

### Branch Strategy
- `main`: Production-ready code, protected branch
- `develop`: Integration branch for features
- `feature/*`: Individual feature branches
- `hotfix/*`: Critical production fixes

### Deployment
- Staging deployments MUST occur before production
- Phased rollouts MUST be used for major features (10% → 50% → 100%)
- Rollback plan MUST be prepared for all releases
- App store submissions MUST include complete release notes

## Governance

### Constitution Authority
This constitution supersedes all other development practices and decisions. When conflicts arise, the principles defined here take precedence.

### Amendments
- Constitution changes require approval from project lead and stakeholder representative
- Amendment proposals MUST include rationale and impact analysis
- Version MUST be incremented using semantic versioning:
  - **MAJOR**: Backward-incompatible principle changes or removals
  - **MINOR**: New principles added or material expansions
  - **PATCH**: Clarifications, wording improvements, non-semantic changes

### Compliance
- All pull requests MUST include a compliance checklist verifying adherence to core principles
- Code reviews MUST verify constitutional compliance before approval (including UML adherence)
- Non-compliance MUST be documented with justification and remediation plan
- Technical debt that violates principles MUST be tracked and addressed within defined timeframes
- **UML diagram deviations MUST be documented with rationale and diagrams updated before merge**

### Continuous Improvement
- Constitution MUST be reviewed quarterly for relevance and effectiveness
- Team retrospectives MUST identify principle violations and root causes
- Lessons learned from production incidents MUST inform constitution updates

**Version**: 1.2.0 | **Ratified**: 2025-12-07 | **Last Amended**: 2025-12-07
