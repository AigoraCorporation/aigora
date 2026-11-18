# ADR-007 — Read-Only gRPC API Foundation

## Status
Accepted

## Context

The Tutor Orchestrator (Java) must query the Curriculum Graph (Python) through a
stable, versioned service boundary. Until v0.2.1 the Curriculum Graph only
loaded, validated, persisted and exported graphs; it exposed no runtime query
API.

Research issue #190 evaluated five questions (RQ-1..RQ-5) and the team approved
a decision lock on 2026-05-17. This ADR records those decisions as binding
architecture and defines the milestones (M1..M5) that release v0.2.2 tracks.

Two constraints shape the design:

- The graph is **read-only during tutoring runtime** (`integration.md`). Writes
  happen only through `PublishGraphUseCase` (ADR-003).
- The persisted Neo4j state written by v0.2.1 is **lossy**: it stores node
  identity, name, domain, description, prerequisite edges and profiles, but not
  `mastery_criteria`, `error_taxonomy` or the graph version. A runtime reader
  cannot rebuild a `CurriculumGraph` from it.

## Decision

### 1. Transport and scope (RQ-1)

The Curriculum Graph exposes a read-only gRPC service
`aigora.curriculum_graph.v1.CurriculumGraphService` with exactly seven RPCs:

| RPC | Purpose |
|-----|---------|
| `GetGraphMetadata` | Active graph version and snapshot summary |
| `GetNode` | Single concept by id |
| `ListNodes` | Concepts, optionally filtered by domain or profile |
| `GetPrerequisites` | Direct prerequisites of a concept (hard, optionally soft) |
| `GetRegressionTargets` | Regression targets of a concept |
| `GetLearningPath` | Shortest prerequisite path between two concepts |
| `HealthCheck` | Serving status, answerable without graph context |

No write, publication, import or export RPCs. No orchestrator-specific
composite RPCs.

### 2. Contract versioning (RQ-2)

- Contracts live in `proto/aigora/curriculum_graph/v1/`. The package
  `aigora.curriculum_graph.v1` is the compatibility boundary.
- Inside `v1` only additive changes are allowed: new RPCs, new fields, new enum
  values that consumers can ignore.
- Removing or renaming RPCs, messages or fields, changing field numbers or
  types, and changing cardinality are breaking and require `v2`.
- Removed tags and names are reserved; deprecation precedes removal.
- A committed contract lock is checked by an automated gate that rejects
  breaking changes to `v1`.

### 3. Error model (RQ-3)

Application errors map one-to-one to gRPC status codes and stable canonical
codes:

| Application error | gRPC status | Canonical code |
|-------------------|-------------|----------------|
| `NODE_NOT_FOUND` | `NOT_FOUND` | `CG_NODE_NOT_FOUND` |
| `PROFILE_NOT_FOUND` | `NOT_FOUND` | `CG_PROFILE_NOT_FOUND` |
| `INVALID_GRAPH_VERSION` | `FAILED_PRECONDITION` | `CG_INVALID_GRAPH_VERSION` |
| `GRAPH_UNAVAILABLE` | `UNAVAILABLE` | `CG_GRAPH_UNAVAILABLE` |
| `INVALID_REQUEST` | `INVALID_ARGUMENT` | `CG_INVALID_REQUEST` |

Every failure carries `code`, `message` (no infrastructure internals),
`request_id`, and `graph_version` when the version context is known.

The taxonomy is closed: no other canonical codes exist in `v1`. When both
endpoints of `GetLearningPath` exist but no path connects them, the RPC
succeeds with an empty path and `path_found = false`; it is not an error.

### 4. `graph_version` invariant (RQ-4)

- Every successful graph-data RPC response carries `graph_version`, including
  empty results.
- Errors include `graph_version` only when the request was bound to a known
  active version; an invalid client-supplied version is never echoed back as if
  valid.
- `HealthCheck` may omit it.
- Partial responses are not allowed.

### 5. Runtime read model: published Neo4j snapshot

The API serves the graph **published in Neo4j**, not the canonical files:

- Publication becomes lossless: node `mastery_criteria` and `error_taxonomy`
  are persisted, and a single `:GraphMetadata` node records the published
  `graph_version`.
- A new application port, `CurriculumGraphReader`, returns the published
  `CurriculumGraph` snapshot. Its Neo4j adapter lives in infrastructure
  (ADR-002 still applies: Cypher stays in infrastructure).
- The API loads the snapshot at startup and answers queries in memory through
  application use cases (`QueryGraphUseCase` and its read-only siblings).
  Neo4j being unreachable or holding no published graph maps to
  `GRAPH_UNAVAILABLE`; `HealthCheck` reports `NOT_SERVING`.
- File-based loading stays the only way to *build* a graph (ADR-001).

### 6. Layering

- Generated protobuf code lives in the contract package
  `aigora.curriculum_graph.v1` and is imported only by the presentation layer.
- gRPC servicers, mappers and the error mapper live in
  `aigora.curriculum_graph.presentation.grpc`.
- Presentation depends on application only (existing import-linter contracts);
  domain and application must not import gRPC, protobuf or the contract
  package.
- The composition root (server bootstrap) is the only place that wires
  infrastructure adapters into application use cases.

### 7. Local runtime (RQ-5)

Docker Compose defines two services: `curriculum-graph-api` (gRPC on `50051`)
and `neo4j` (`7474`, `7687`), configured through `NEO4J_URI`, `NEO4J_USER`,
`NEO4J_PASSWORD`, `GRPC_PORT` and optional `GRAPH_VERSION_DEFAULT`. The API
starts only after Neo4j is healthy, and readiness requires both health checks.
A clean checkout must validate with `docker compose up` plus `grpcurl` smoke
tests.

## Consequences

### Positive

- The Tutor Orchestrator gets a stable, versioned, typed boundary.
- Breaking contract changes are caught mechanically.
- Error handling is uniform and observable across RPCs.
- Every answer is bound to a graph version, so decisions are reproducible.
- In-memory serving reuses the tested traversal logic and keeps latency low.

### Negative

- Publication changes (new persisted properties, `:GraphMetadata`) require
  republishing existing graphs.
- The API serves the snapshot loaded at startup; picking up a newly published
  graph requires a restart (acceptable while graphs change only at release
  time).
- Generated code and a contract lock must be kept in sync with the `.proto`.

## Dependencies

- ADR-001 — Graph Loader Remains File-Based
- ADR-002 — Neo4j Persistence via Repository Port
- ADR-003 — Graph Publication Use Case Is the Entrypoint
- ADR-004 — Use Command / Result Contracts for Use Cases

No cycles: this ADR depends only on accepted v0.2.1 ADRs.

## Milestones (Required)

| ID | Description | Issues | Status | Owner |
|----|-------------|--------|--------|-------|
| M1 | Define v1 gRPC contract boundary and versioning policy | #193, #194, #195 | In Progress | @brunolnetto |
| M2 | Implement delivery adapter mapping requests/responses to use cases | #196, #202 | Planned | @brunolnetto |
| M3 | Standardize error model and response invariants | #197 | Planned | @brunolnetto |
| M4 | Define Dockerized local runtime contract (API + Neo4j) | #200 | Planned | @brunolnetto |
| M5 | Define validation and release readiness gates | #198, #199, #203 | Planned | @brunolnetto |

Support work without milestone linkage: #190 (research baseline, closed by this
ADR), #201 (local validation playbook).

Milestone order follows the release DAG:
M1 → M2 → M3 → {M4, M5}. See
`docs/06-engineering/governance/releases/v0.2.2-implementation-dag.md`.

## Notes

- Research baseline and decision lock: #190.
- Release umbrella: #186.
- Previously referenced as `ADR-TBD-GRPC-FOUNDATION`.
