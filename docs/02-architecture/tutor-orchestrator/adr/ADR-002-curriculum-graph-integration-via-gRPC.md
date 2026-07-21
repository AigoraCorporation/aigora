# ADR-002 — Curriculum Graph Integration via gRPC

## Status

Accepted

## Context

The Tutor Orchestrator requires access to curriculum topology information in order to generate and evaluate learning candidates.

The Curriculum Graph is the authoritative owner of:

* curriculum topology
* prerequisite relationships
* dependency relationships
* graph traversal
* curriculum versioning

Embedding curriculum topology logic directly into the Tutor Orchestrator would:

* violate bounded context ownership
* increase coupling
* duplicate graph logic
* create multiple sources of truth
* reduce maintainability
* make independent evolution more difficult

The architecture requires a clear separation between pedagogical decision-making and curriculum topology management.

## Decision

The Tutor Orchestrator must access curriculum topology exclusively through the Curriculum Graph API.

Communication between the Tutor Orchestrator and Curriculum Graph must occur through explicit gRPC contracts.

The Curriculum Graph API must:

* expose topology retrieval capabilities
* expose graph traversal capabilities
* expose prerequisite resolution capabilities
* expose graph version information
* encapsulate graph persistence details

The Tutor Orchestrator must:

* consume topology information through gRPC contracts
* remain independent from graph storage implementation
* treat Curriculum Graph as an external dependency
* own pedagogical decision-making exclusively

The Tutor Orchestrator must not:

* access Neo4j directly
* execute Cypher queries
* duplicate curriculum topology logic
* own graph traversal logic
* own graph persistence concerns

## Consequences

### Positive

* clear bounded context ownership
* reduced coupling
* independent service evolution
* language independence between services
* explicit integration contracts
* improved maintainability
* infrastructure encapsulation
* easier testing through contract boundaries

### Negative

* additional network hop
* dependency on service availability
* gRPC contract maintenance overhead
* distributed system complexity

## Constraints

* Curriculum Graph remains the single source of truth for topology
* Tutor Orchestrator must never access Neo4j directly
* all topology operations must pass through gRPC contracts
* graph persistence must remain encapsulated within Curriculum Graph
* pedagogical decisions must remain owned by Tutor Orchestrator
* Curriculum Graph must not perform pedagogical decisions
