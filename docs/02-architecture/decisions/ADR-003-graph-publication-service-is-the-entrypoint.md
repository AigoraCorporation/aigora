# ADR-003 — GraphPublicationService as Orchestrator

## Status
Accepted

## Context

Graph publication involves multiple steps:
- loading data
- validation
- transformation
- persistence

Without a clear entry point, logic becomes fragmented.

## Decision

GraphPublicationService is the single orchestration entry point.

It MUST:
- coordinate the full publication flow
- delegate responsibilities to other components

It MUST NOT:
- implement persistence directly
- contain domain logic

## Consequences

### Positive
- clear flow ownership
- improved maintainability
- predictable execution

### Negative
- requires strict discipline in responsibilities

## Constraints

- persistence MUST be delegated to GraphRepository
- business rules MUST remain in domain layer