# ADR-003 — Graph Publication Use Case Is the Entry Point

## Status
Accepted

## Context

Graph publication involves multiple steps:

- loading graph data
- validating graph structure
- optionally exporting graph snapshots
- persisting graph data
- validating persisted state

Earlier designs used a dedicated publication service as the primary orchestration entry point. After the architecture was refactored around explicit use cases, keeping a separate service for a single publication flow added unnecessary indirection.

## Decision

`PublishGraphUseCase` is the application entry point for graph publication.

It must:

- receive a `PublishGraphCommand`
- orchestrate graph loading and publication
- depend on repository contracts and application ports
- return a `PublishGraphResult`

It must not:

- execute Cypher directly
- instantiate concrete infrastructure adapters directly
- contain domain entity invariants
- act as an HTTP controller or API schema

## Consequences

### Positive

- publication has a clear application boundary
- orchestration is easier to test
- external adapters can call the use case consistently
- the old service layer no longer adds unnecessary indirection

### Negative

- dependency wiring must be handled outside the use case
- future shared publication behavior may require extracting a service again if multiple publication workflows emerge

## Constraints

- persistence must be delegated to `CurriculumGraphRepository`
- Neo4j-specific behavior must remain in infrastructure
- external adapters must call the use case, not the repository directly
