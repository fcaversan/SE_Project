# Feature Specification: Remote Controls (FR-RMC)

**Feature ID**: 002-remote-controls  
**Priority**: P1 (High Priority)  
**Status**: Draft  
**Created**: December 7, 2025  
**SRS Reference**: FR-RMC-001 through FR-RMC-010

---

## Overview

This feature enables users to remotely control their vehicle's locks, climate system, and trunk/frunk via the mobile application. All commands are sent through the backend API to the vehicle's Telematics Control Unit (TCU).

**Business Value**: Remote controls are essential convenience features that significantly enhance the user experience. Remote climate preconditioning before entering the vehicle is particularly valuable for electric vehicles.

**Dependencies**: 
- Home Screen feature (001) for vehicle state display
- Backend API with vehicle command endpoints
- VehicleDataService for command execution

---

## User Stories

### User Story 1: Remote Lock/Unlock Vehicle (Priority: P1)

**As a** vehicle owner  
**I want to** remotely lock and unlock my vehicle from the app  
**So that** I can secure my vehicle from anywhere or grant access without being physically present

**Acceptance Criteria**:
- User can tap "Lock" button to remotely lock all doors
- User can tap "Unlock" button to remotely unlock all doors
- Lock/unlock commands complete within 3 seconds (NFR-PERF-001)
- Success/failure feedback displayed immediately
- Haptic feedback provided on successful lock/unlock (FR-RMC-010)
- Current lock status updates on home screen after command
- Warning shown if vehicle is unlocked for >10 minutes

**Functional Requirements Covered**: FR-RMC-001, FR-RMC-002, FR-RMC-010

---

### User Story 2: Remote Climate Control (Priority: P1)

**As a** vehicle owner  
**I want to** remotely activate climate control and set cabin temperature  
**So that** my vehicle is at a comfortable temperature when I enter it

**Acceptance Criteria**:
- User can turn climate control On/Off remotely
- User can set target temperature (range: 15°C - 28°C or 59°F - 82°F)
- Temperature displayed in user's preferred unit (°C/°F)
- Warning shown if vehicle not plugged in (battery drain)
- Climate status updates on home screen
- Visual indicator shows climate is actively running
- User can see estimated battery consumption

**Functional Requirements Covered**: FR-RMC-003, FR-RMC-004, FR-RMC-007

---

### User Story 3: Heated Seats & Steering Wheel Control (Priority: P2)

**As a** vehicle owner  
**I want to** remotely activate heated seats and heated steering wheel  
**So that** my vehicle is warm and comfortable in cold weather

**Acceptance Criteria**:
- User can enable/disable front left heated seat
- User can enable/disable front right heated seat
- User can enable/disable rear heated seats (if equipped)
- User can enable/disable heated steering wheel (if equipped)
- Heated seat levels: Off, Low, Medium, High
- Controls only available when climate is active
- Warning shown if vehicle not plugged in

**Functional Requirements Covered**: FR-RMC-005

---

### User Story 4: Defrost Activation (Priority: P2)

**As a** vehicle owner  
**I want to** remotely activate front and rear defrosters  
**So that** my windows are clear when I enter the vehicle in cold/foggy weather

**Acceptance Criteria**:
- User can activate front defroster remotely
- User can activate rear defroster remotely
- Defrost controls only available when climate is active
- Auto-deactivates after 15 minutes for safety
- Visual indicator shows defroster status

**Functional Requirements Covered**: FR-RMC-006

---

### User Story 5: Remote Trunk/Frunk Opening (Priority: P2)

**As a** vehicle owner  
**I want to** remotely open the trunk (rear) or frunk (front trunk)  
**So that** I can access storage without using the key or being inside the vehicle

**Acceptance Criteria**:
- User can remotely open rear trunk
- User can remotely open front trunk (frunk)
- Confirmation dialog shown before opening
- Warning shown if vehicle is moving (command rejected)
- Status indicator shows if trunk/frunk is open
- Cannot open while vehicle is locked (must unlock first)

**Functional Requirements Covered**: FR-RMC-008

---

### User Story 6: Locate Vehicle (Honk & Flash) (Priority: P3)

**As a** vehicle owner  
**I want to** make my vehicle honk and flash its lights  
**So that** I can locate it in a parking lot or garage

**Acceptance Criteria**:
- User can trigger honk & flash from app
- Horn honks 3 times
- Lights flash 3 times
- Command works regardless of lock status
- Cooldown period of 10 seconds between activations
- Visual feedback in app when command sent

**Functional Requirements Covered**: FR-RMC-009

---

## Key Entities

### RemoteCommand
- `command_id`: Unique identifier (UUID)
- `command_type`: Enum (LOCK, UNLOCK, CLIMATE_ON, CLIMATE_OFF, etc.)
- `parameters`: Dict (e.g., target_temp for climate)
- `status`: Enum (PENDING, SUCCESS, FAILED, TIMEOUT)
- `timestamp`: DateTime of command initiation
- `response_time`: Time to complete (milliseconds)
- `error_message`: Optional error description

### ClimateSettings
- `is_active`: Boolean
- `target_temp_celsius`: Float (15-28°C)
- `front_left_seat_heat`: Enum (OFF, LOW, MEDIUM, HIGH)
- `front_right_seat_heat`: Enum (OFF, LOW, MEDIUM, HIGH)
- `rear_seat_heat`: Enum (OFF, LOW, MEDIUM, HIGH)
- `steering_wheel_heat`: Boolean
- `front_defrost`: Boolean
- `rear_defrost`: Boolean
- `is_plugged_in`: Boolean (read-only)

### TrunkStatus
- `front_trunk_open`: Boolean
- `rear_trunk_open`: Boolean

---

## Success Criteria

### Performance
- Lock/unlock commands complete within 3 seconds
- Climate commands complete within 5 seconds
- Command success rate ≥99.9% (NFR-REL-003)
- Haptic feedback within 100ms of success

### Usability
- Remote controls accessible from home screen with max 1 tap
- Clear visual feedback for all command states (pending, success, failure)
- Warning messages for unsafe operations (unplugged preconditioning, moving vehicle)
- Temperature slider intuitive and responsive

### Reliability
- Offline detection: Show cached state with "offline" indicator
- Command queue: Retry failed commands up to 3 times
- Timeout handling: Mark command failed after 10 seconds
- State synchronization: Refresh vehicle state after successful command

---

## Edge Cases & Error Handling

### Network Errors
- **Case**: No internet connection
- **Behavior**: Show "offline" banner, disable command buttons, display cached state

### Vehicle Offline
- **Case**: Vehicle has no cellular connection
- **Behavior**: Command times out after 10s, show error "Unable to reach vehicle"

### Conflicting Commands
- **Case**: User sends multiple commands rapidly
- **Behavior**: Queue commands, execute sequentially, show "Command in progress..."

### Battery Protection
- **Case**: User tries to precondition when not plugged in and battery <20%
- **Behavior**: Show warning dialog "This will reduce range by ~15km. Continue?"

### Safety Restrictions
- **Case**: User tries to open trunk while vehicle is moving
- **Behavior**: Reject command, show error "Cannot open trunk while vehicle is in motion"

### Feature Availability
- **Case**: Vehicle doesn't have heated seats/steering wheel
- **Behavior**: Hide unavailable features in UI based on vehicle capabilities

---

## UI/UX Requirements

### Remote Controls Page (`/controls`)
- Large, touch-friendly buttons for primary actions
- Lock/Unlock toggle with icon indicator
- Climate control card with:
  - On/Off toggle
  - Temperature slider (visual + numeric)
  - Quick preset buttons (18°C, 21°C, 24°C)
  - Heated seats icons (left, right, rear)
  - Heated steering wheel icon
  - Defrost toggles (front, rear)
  - Battery drain estimate
- Trunk/Frunk card with open buttons
- Locate vehicle button (honk & flash)

### Visual Feedback
- Loading spinner during command execution
- Green checkmark on success
- Red X on failure
- Haptic feedback (vibration) on lock/unlock success
- Toast notifications for command results

### Responsive Design
- Mobile-first (portrait orientation)
- Tablet support (landscape with grid layout)
- Desktop support (centered card layout, max-width 800px)

---

## Non-Functional Requirements

### Performance (NFR-PERF)
- Command response time <3s (lock/unlock)
- Command response time <5s (climate)
- Page load time <2s
- Smooth animations (60fps)

### Security (NFR-SEC)
- All commands require authentication
- Commands encrypted in transit (TLS 1.2+)
- Command authorization validated server-side
- Audit log of all remote commands

### Usability (NFR-USA)
- Primary functions accessible with 1 tap from home
- Confirmation dialogs for destructive actions
- Clear error messages in user-friendly language
- Color-blind friendly indicators (icons + text)

---

## Testing Requirements

### Unit Tests
- RemoteCommandService: send_command, get_status, cancel_command
- ClimateSettings: validation, temperature conversion, defaults
- Mock responses for all command types
- Error handling for timeouts, network failures

### Integration Tests
- Flask API endpoints for all remote commands
- Command execution flow (pending → success/failed)
- State synchronization after commands
- Error response handling

### Test Coverage Target
- ≥85% code coverage
- All command types tested
- All error paths tested
- Edge cases covered

---

## Dependencies & Prerequisites

### Technical Dependencies
- Flask backend with command queue
- VehicleDataService with command execution methods
- WebSocket or polling for real-time status updates
- Mock service with command simulation

### Feature Dependencies
- Home Screen (001) must be complete
- Vehicle state models extended with climate/trunk data
- User authentication in place

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Extend VehicleState model with climate/trunk fields
- Create RemoteCommandService with mock implementation
- Add command history tracking
- API endpoints for lock/unlock

### Phase 2: Core Controls (Week 2)
- Lock/Unlock UI and logic
- Climate On/Off UI and logic
- Temperature control slider
- Battery drain warnings

### Phase 3: Advanced Climate (Week 3)
- Heated seats controls
- Heated steering wheel
- Defrost controls
- Preconditioning status display

### Phase 4: Trunk & Locate (Week 4)
- Trunk/Frunk controls
- Honk & Flash feature
- Confirmation dialogs
- Safety restrictions

### Phase 5: Polish & Testing (Week 5)
- Unit tests (≥85% coverage)
- Integration tests
- Error handling refinement
- Performance optimization
- UI polish and animations

---

## Out of Scope

- Real vehicle API integration (mock-only for prototype)
- Command scheduling (e.g., "Start climate at 7 AM")
- Geofence-based auto-lock/unlock
- Valet mode activation
- Speed limit enforcement
- Battery charging commands (separate feature: FR-CHG)
- Window control (not in SRS)

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Command timeout | High | Medium | Implement retry logic, clear timeout messages |
| Battery drain concern | Medium | Low | Prominent warnings, estimate consumption |
| Conflicting commands | Medium | Low | Command queue, sequential execution |
| Network latency | Medium | Medium | Loading indicators, optimistic UI updates |
| Safety issues (trunk while moving) | High | Low | Server-side validation, reject unsafe commands |

---

## Metrics & KPIs

### Success Metrics
- Command success rate ≥99.5%
- Average command response time <3s
- User satisfaction score ≥4.5/5
- Feature usage rate ≥80% of active users

### Performance Metrics
- API endpoint response time <500ms
- UI responsiveness (time to interactive) <2s
- Command queue processing time <100ms

---

## Acceptance Sign-Off

This specification is ready for implementation when:
- [x] All user stories defined with acceptance criteria
- [x] Technical requirements documented
- [x] UI/UX requirements specified
- [x] Edge cases identified
- [x] Testing strategy defined
- [ ] Stakeholder review complete
- [ ] Technical feasibility confirmed

**Next Steps**: Create implementation plan and task breakdown using `/speckit.plan` and `/speckit.tasks`.
