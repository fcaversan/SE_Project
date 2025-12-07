# Software Requirements Specification
## Vehicle Connect Mobile Application

**Version:** 1.1  
**Date:** October 9, 2025  
**Prepared for:** Vehicle Engineering Division  
**Prepared by:** Gemini Systems

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 Purpose
   - 1.2 Document Conventions
   - 1.3 Intended Audience and Reading Suggestions
   - 1.4 Product Scope
   - 1.5 Overview
   - 1.6 References
2. [Overall Description](#2-overall-description)
   - 2.1 Product Perspective
   - 2.2 Product Functions
   - 2.3 User Characteristics
   - 2.4 Constraints
   - 2.5 Assumptions and Dependencies
   - 2.6 Apportioning of Requirements
3. [Specific Requirements](#3-specific-requirements)
   - 3.1 External Interface Requirements
   - 3.2 Functional Requirements
   - 3.3 Non-Functional Requirements
4. [Appendix A: Glossary](#appendix-a-glossary)

---

## 1. Introduction

This section provides an overview of the Software Requirements Specification (SRS) for the Vehicle Connect Mobile Application.

### 1.1 Purpose

The purpose of this document is to provide a detailed description of the requirements for the Vehicle Connect mobile application. It will serve as the guiding document for the design, development, and testing of the software. This SRS defines the functional and non-functional requirements of the system and establishes the agreement between the stakeholders (Vehicle Engineering) and the development team.

### 1.2 Document Conventions

This SRS document adheres to the IEEE 830-1998 standard. Functional requirements are uniquely identified with the prefix FR- followed by a category code and a number (e.g., FR-CHG-001). Non-functional requirements are identified with the prefix NFR-. The keyword "shall" is used to denote a mandatory requirement.

### 1.3 Intended Audience and Reading Suggestions

This document is intended for:

- **Project Managers**: To understand the scope and plan the project.
- **Software Developers**: To understand the specific features to be built.
- **QA & Testing Teams**: To create test cases that verify the functionality.
- **Stakeholders (Vehicle Engineering)**: To review and confirm that the requirements accurately capture their needs.

It is recommended to read Sections 1 and 2 for a high-level overview before delving into the detailed requirements in Section 3.

### 1.4 Product Scope

The Vehicle Connect application is a mobile client for iOS and Android platforms that will provide vehicle owners with the ability to remotely monitor, control, and manage their electric vehicle. The scope of this SRS is limited to the mobile application itself. It does not cover the vehicle's onboard telematics unit or the backend cloud infrastructure, which are considered external systems with which this application will interact.

### 1.5 Overview

This SRS is organized into three main sections. Section 1 provides an introduction, scope, and overview of the document. Section 2 gives an overall description of the product, its constraints, and its dependencies. Section 3 details the specific functional and non-functional requirements that the software must satisfy. The document concludes with a glossary and an index for ease of reference.

### 1.6 References

- User Requirements Document: Vehicle Connect Mobile App, Version 1.0, October 6, 2025.
- IEEE Std 830-1998, Recommended Practice for Software Requirements Specifications.

---

## 2. Overall Description

### 2.1 Product Perspective

The Vehicle Connect app is a component of a larger vehicle ecosystem. It is a client application that communicates via a secure API with a central backend server. This server, in turn, communicates with the vehicle's Telematics Control Unit (TCU). The application will not communicate directly with the vehicle, with the exception of proximity-based functions like Phone as a Key (PaaK) which will use Bluetooth Low Energy (BLE) or Ultra-Wideband (UWB).

### 2.2 Product Functions

The major functions of the Vehicle Connect application are summarized as follows:

- Real-time vehicle status monitoring (SoC, range, location).
- Comprehensive charging management (remote control, scheduling, station finding).
- Remote vehicle controls (climate, locks, trunk).
- Vehicle health and diagnostic information display.
- Intelligent trip planning with integrated charging stops.
- Secure key and access management.

### 2.3 User Characteristics

The primary user is the vehicle owner. This user is assumed to be familiar with using modern mobile applications but is not expected to have technical knowledge of the vehicle's internal systems. The application's interface must be intuitive and straightforward. Secondary users may include family members or other temporary drivers granted access by the primary owner.

### 2.4 Constraints

- The application shall be developed for modern iOS and Android operating systems.
- All communication between the mobile app and the backend server shall be encrypted using industry-standard protocols (e.g., TLS 1.2 or higher).
- The app must authenticate the user securely before allowing access to vehicle data or controls.
- The application must comply with all relevant data privacy regulations (e.g., GDPR, CCPA).

### 2.5 Assumptions and Dependencies

- The user's mobile device has a stable internet connection (Wi-Fi or cellular) for most remote functions.
- The vehicle is equipped with a functioning Telematics Control Unit (TCU) and has an active data connection.
- A secure backend API for communication between the app and the vehicle systems exists and is documented.
- Third-party services for maps and charging station data will be available and reliable.

### 2.6 Apportioning of Requirements

All functional and non-functional requirements detailed in this document are considered part of the initial release (Version 1.0) unless explicitly noted otherwise. There are currently no requirements designated to be delayed until future versions.

---

## 3. Specific Requirements

### 3.1 External Interface Requirements

**User Interfaces**: The application shall feature a clean, modern user interface that is consistent with the brand's design language. The UI must be optimized for both light and dark modes and be responsive to various screen sizes on supported devices.

**Software Interfaces**: The application shall interface with:
- The Vehicle Backend API for all vehicle data and remote commands.
- A third-party mapping service (e.g., Google Maps, Apple Maps) for navigation and location features.
- A third-party payment gateway for in-app charging payments.
- The mobile device's operating system for push notifications, GPS, and Bluetooth/UWB services.

### 3.2 Functional Requirements

#### 3.2.1 FR-HSS: Home Screen & Vehicle Status

- **FR-HSS-001**: The system shall display the vehicle's current State of Charge (SoC) as a percentage value on the application's home screen.
- **FR-HSS-002**: The system shall display a visual representation of the vehicle's battery level.
- **FR-HSS-003**: The system shall display an estimated vehicle range in the user's preferred unit (miles or kilometers).
- **FR-HSS-004**: The estimated vehicle range calculation shall be based on the vehicle's current SoC, recent energy consumption trends, and the current ambient temperature reported by the vehicle.
- **FR-HSS-005**: The system shall display the vehicle's current lock status (Locked/Unlocked).
- **FR-HSS-006**: The system shall display the vehicle's interior cabin temperature as reported by the vehicle.
- **FR-HSS-007**: The system shall indicate whether the climate control system is currently active.
- **FR-HSS-008**: The system shall display a clear, graphical representation of the user's vehicle on the home screen.

#### 3.2.2 FR-CHG: Charging Management

- **FR-CHG-001**: The system shall allow the user to remotely start a charging session if the vehicle is plugged into a compatible charger.
- **FR-CHG-002**: The system shall allow the user to remotely stop a charging session.
- **FR-CHG-003**: During an active charging session, the system shall display: current SoC, estimated time to completion, current charging rate (kW), and supplied voltage/amperage.
- **FR-CHG-004**: The system shall provide an interface for the user to set a maximum charging limit as a percentage. The interface shall default to 80% for daily charging and shall provide a convenient one-time "charge to 100%" option for trips.
- **FR-CHG-005**: The system shall allow the user to create, edit, and delete charging schedules, defining a start time or a desired ready-by time.
- **FR-CHG-006**: The system shall display a map of charging stations.
- **FR-CHG-007**: The system shall allow the user to filter charging stations by connector type and power level (kW).
- **FR-CHG-008**: The system shall display real-time availability for charging stations where the data is provided by the network operator.

#### 3.2.3 FR-RMC: Remote Controls

- **FR-RMC-001**: The system shall allow the user to remotely lock the vehicle's doors.
- **FR-RMC-002**: The system shall allow the user to remotely unlock the vehicle's doors.
- **FR-RMC-003**: The system shall allow the user to remotely activate the vehicle's climate control system (HVAC).
- **FR-RMC-004**: The system shall allow the user to set a target temperature for the cabin.
- **FR-RMC-005**: The system shall allow the user to remotely activate/deactivate heated seats and the heated steering wheel, if equipped.
- **FR-RMC-006**: The system shall allow the user to remotely activate front and rear defrosters.
- **FR-RMC-007**: The system shall display a warning to the user if they attempt to precondition the cabin while the vehicle is not plugged in, indicating the action will consume battery range.
- **FR-RMC-008**: The system shall allow the user to remotely open the front trunk (frunk) and rear trunk.
- **FR-RMC-009**: The system shall provide a function to remotely honk the horn and flash the lights.
- **FR-RMC-010**: The system shall provide haptic feedback on the user's mobile device upon successful completion of a remote lock or unlock command.

#### 3.2.4 FR-VHD: Vehicle Health & Details

- **FR-VHD-001**: The system shall display the individual pressure of each tire as reported by the TPMS.
- **FR-VHD-002**: The system shall visually flag any tire whose pressure is outside the recommended range.
- **FR-VHD-003**: The system shall display the vehicle's total odometer reading.
- **FR-VHD-004**: The system shall display a qualitative indicator of the high-voltage battery's internal temperature (e.g., Cold, Optimal, Hot).
- **FR-VHD-005**: The system shall display any active service alerts or diagnostic trouble codes from the vehicle in a human-readable format.

#### 3.2.5 FR-TRP: Trip & Driving Analytics

- **FR-TRP-001**: The system shall allow the user to search for a destination within the app and send it to the vehicle's in-car navigation system.
- **FR-TRP-002**: The system shall provide a trip planner that calculates a route to a destination, automatically adding required charging stops.
- **FR-TRP-003**: The trip planner's calculation shall consider the vehicle's current SoC, route topography (elevation changes), and charger power levels to estimate charging times.
- **FR-TRP-004**: The system shall display historical trip data, including energy consumption (e.g., kWh/100km or Wh/mile) and energy recaptured via regenerative braking.

#### 3.2.6 FR-SEC: Security & Access Management

- **FR-SEC-001**: The system shall support a Phone as a Key (PaaK) feature, allowing the authenticated app to unlock and start the vehicle via proximity (BLE/UWB).
- **FR-SEC-002**: The system shall allow the primary user to invite other users to have digital key access to the vehicle.
- **FR-SEC-003**: The primary user shall be able to revoke digital key access at any time.
- **FR-SEC-004**: The system shall allow the primary user to apply restrictions to secondary keys, such as a maximum speed limit or a defined geographical boundary (geo-fence).
- **FR-SEC-005**: The system shall allow the user to remotely activate and deactivate the vehicle's Sentry/Surveillance Mode.
- **FR-SEC-006**: The system shall send a push notification to the user if a Sentry Mode event is triggered.
- **FR-SEC-007**: The system shall allow the user to view recorded camera footage from triggered Sentry Mode events.
- **FR-SEC-008**: The system shall display the vehicle's current GPS location on a map.

#### 3.2.7 FR-USR: User Profile & Notifications

- **FR-USR-001**: The system shall allow the user to configure their preferred units (e.g., miles/km, °F/°C).
- **FR-USR-002**: The system shall allow the user to manage notification settings, enabling/disabling alerts for events such as:
  - Charging started/completed/interrupted.
  - Vehicle unlocked.
  - Sentry mode event.
- **FR-USR-003**: The user shall be able to manage their account profile and payment methods for charging services.

### 3.3 Non-Functional Requirements

#### 3.3.1 NFR-PERF: Performance Requirements

- **NFR-PERF-001**: A remote command (e.g., lock, start climate) sent from the app shall receive a success/fail confirmation from the server and display it in the UI within 3 seconds under normal network conditions.
- **NFR-PERF-002**: Vehicle status data displayed on the home screen shall be updated from the vehicle and reflect a state no older than 60 seconds from the time of the last successful data poll.
- **NFR-PERF-003**: The application shall launch from a cold start to a usable home screen within 4 seconds.

#### 3.3.2 NFR-SEC: Security Requirements

- **NFR-SEC-001**: User authentication shall be required upon app launch, using biometrics (Face ID/fingerprint) or a PIN.
- **NFR-SEC-002**: All sensitive data stored locally on the device (e.g., authentication tokens, user credentials) shall be encrypted.
- **NFR-SEC-003**: The application shall implement certificate pinning to prevent man-in-the-middle attacks when communicating with the backend API.

#### 3.3.3 NFR-REL: Reliability Requirements

- **NFR-REL-001**: The core application functions shall have an uptime of 99.9%.
- **NFR-REL-002**: The system shall handle loss of network connectivity gracefully, informing the user that the device is offline and that remote commands are unavailable. Cached data may be shown with a "last updated" timestamp.
- **NFR-REL-003**: Critical remote commands (lock, unlock) shall have a success rate of 99.9% under standard operating conditions (vehicle and phone have stable connectivity).

#### 3.3.4 NFR-USA: Usability Requirements

- **NFR-USA-001**: The application shall adhere to the platform-specific human interface guidelines for iOS and Android.
- **NFR-USA-002**: The primary functions (lock/unlock, climate, charge status) shall be accessible from the main screen with no more than one tap.

---

## Appendix A: Glossary

- **API**: Application Programming Interface
- **BLE**: Bluetooth Low Energy
- **CAN bus**: Controller Area Network bus; a vehicle bus standard.
- **HVAC**: Heating, Ventilation, and Air Conditioning
- **PaaK**: Phone as a Key
- **SoC**: State of Charge; the level of charge of an electric battery relative to its capacity.
- **SRS**: Software Requirements Specification
- **TCU**: Telematics Control Unit
- **TPMS**: Tire Pressure Monitoring System
- **UWB**: Ultra-Wideband
