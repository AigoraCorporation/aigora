# ADR-002 — Neo4j Persistence via Repository Port

## Status
Accepted

## Context

Direct usage of Neo4j across the codebase leads to:
- tight coupling
- scattered Cypher queries
- difficult testing

## Decision

All Neo4j persistence MUST go through the GraphRepository port.

Concrete implementation:
- Neo4jGraphRepository (infrastructure layer)

## Consequences

### Positive
- centralized persistence logic
- improved testability
- easier refactoring

### Negative
- additional abstraction layer

## Constraints

- Cypher MUST NOT appear outside infrastructure
- Application layer MUST depend on ports only
- Domain MUST NOT depend on Neo4j