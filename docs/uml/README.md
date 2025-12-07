# UML Design Documentation

This directory contains PlantUML (`.puml`) diagrams that define the architecture and design of the Vehicle Connect application.

## Directory Structure

- **`class/`** - Class diagrams defining Python class structures, attributes, methods, and relationships
- **`activity/`** - Activity diagrams defining workflows and business logic flows
- **`sequence/`** - Sequence diagrams defining component interactions and API call sequences

## Usage

These diagrams are **authoritative design specifications**. All implementation MUST follow these designs as per Constitution Principle VIII (Design-Driven Implementation).

### Viewing Diagrams

You can view PlantUML diagrams using:

1. **Online**: [PlantUML Web Server](http://www.plantuml.com/plantuml/uml/)
2. **VS Code Extension**: Install "PlantUML" extension
3. **Local**: Install PlantUML locally with Java

### Updating Diagrams

When making design changes:

1. Update the relevant `.puml` file(s) first
2. Get design review/approval
3. Then implement the code changes
4. Code review MUST verify implementation matches updated diagrams

## Design Principles

- All Python classes defined in code MUST have corresponding class diagrams
- All multi-step workflows MUST have activity diagrams
- All component interactions MUST have sequence diagrams
- Deviations from diagrams MUST be documented with rationale
