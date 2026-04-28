# ADR-001 — GraphLoader Remains File-Based

## Status
Accepted

## Context

The system requires a deterministic and reproducible way to load graph data.

Introducing persistence or external dependencies into the loading process would:
- increase coupling
- reduce testability
- break reproducibility

## Decision

GraphLoader MUST remain strictly file-based.

It MUST:
- read from files only
- not access databases
- not depend on infrastructure components

## Consequences

### Positive
- deterministic behavior
- easy testing
- clear separation of concerns

### Negative
- requires separate step for persistence

## Constraints

- GraphLoader MUST NOT access Neo4j
- GraphLoader MUST NOT contain persistence logic