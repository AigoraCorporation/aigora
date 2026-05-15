# ADR-002 — Neo4j Persistence via Repository Port

## Status
Accepted

## Context

Direct usage of Neo4j across the codebase would lead to:

- tight coupling
- scattered Cypher queries
- difficult testing
- infrastructure leakage into application and domain code

## Decision

All Neo4j persistence must go through the `CurriculumGraphRepository` port.

Concrete implementation:

- `Neo4jCurriculumGraphRepository` in the infrastructure layer

## Consequences

### Positive

- centralized persistence logic
- improved testability
- easier replacement of persistence technology
- clear dependency inversion

### Negative

- additional abstraction layer
- dependency wiring must be explicit

## Constraints

- Cypher must not appear outside infrastructure
- application code must depend on repository contracts only
- domain code must not depend on Neo4j
- Neo4j-specific validation belongs to infrastructure
