# Curriculum Graph gRPC API — Contract v1

**Status:** Frozen (v0.2.2)
**Source of truth:** [`proto/aigora/curriculum_graph/v1/curriculum_graph.proto`](../../../proto/aigora/curriculum_graph/v1/curriculum_graph.proto)
**Decision record:** [ADR-007](adr/ADR-007-read-only-grpc-api-foundation.md)

This document describes the frozen v1 contract of the read-only Curriculum
Graph API and the rules that keep it backward compatible. Field-level reference
documentation is generated from the `.proto` file.

---

## Service

`aigora.curriculum_graph.v1.CurriculumGraphService`

| RPC | Request → Response | Purpose | Canonical errors |
|-----|-------------------|---------|------------------|
| `GetGraphMetadata` | `GetGraphMetadataRequest` → `GetGraphMetadataResponse` | Active version, counts, profiles, domains | `CG_INVALID_GRAPH_VERSION`, `CG_GRAPH_UNAVAILABLE` |
| `GetNode` | `GetNodeRequest` → `GetNodeResponse` | One concept by id | `CG_NODE_NOT_FOUND`, `CG_INVALID_REQUEST`, `CG_INVALID_GRAPH_VERSION`, `CG_GRAPH_UNAVAILABLE` |
| `ListNodes` | `ListNodesRequest` → `ListNodesResponse` | Concepts by id order, filter by domain/profile, paginated | `CG_PROFILE_NOT_FOUND`, `CG_INVALID_REQUEST`, `CG_INVALID_GRAPH_VERSION`, `CG_GRAPH_UNAVAILABLE` |
| `GetPrerequisites` | `GetPrerequisitesRequest` → `GetPrerequisitesResponse` | Direct prerequisites with kind (hard/soft) | `CG_NODE_NOT_FOUND`, `CG_INVALID_REQUEST`, `CG_INVALID_GRAPH_VERSION`, `CG_GRAPH_UNAVAILABLE` |
| `GetRegressionTargets` | `GetRegressionTargetsRequest` → `GetRegressionTargetsResponse` | Concepts to revisit when mastery breaks down | `CG_NODE_NOT_FOUND`, `CG_INVALID_REQUEST`, `CG_INVALID_GRAPH_VERSION`, `CG_GRAPH_UNAVAILABLE` |
| `GetLearningPath` | `GetLearningPathRequest` → `GetLearningPathResponse` | Shortest prerequisite path, start to target | `CG_NODE_NOT_FOUND`, `CG_INVALID_REQUEST`, `CG_INVALID_GRAPH_VERSION`, `CG_GRAPH_UNAVAILABLE` |
| `HealthCheck` | `HealthCheckRequest` → `HealthCheckResponse` | `SERVING` / `NOT_SERVING` | none |

The set is closed for v1: no write, publication, import, export or
orchestrator-specific composite RPCs.

---

## Semantics

### Request context

Graph-data requests carry an optional `RequestContext`:

- `request_id` — correlation id; the server generates one when empty.
- `graph_version` — the version the caller expects; empty means the active
  version. A mismatch fails with `CG_INVALID_GRAPH_VERSION`.

### `graph_version` invariant

| RPC | Success | Error |
|-----|---------|-------|
| `GetGraphMetadata`, `GetNode`, `ListNodes`, `GetPrerequisites`, `GetRegressionTargets`, `GetLearningPath` | Always present, also for empty results | Present only when the request was bound to the known active version |
| `HealthCheck` | Present when a snapshot is loaded | — |

An invalid client-supplied version is never echoed back as `graph_version`.

### Relationship semantics

- Prerequisite edges point from the prerequisite to the dependent concept.
  `GetPrerequisites(X)` returns the sources of hard (and, unless
  `include_soft = false`, soft) edges whose target is `X`.
- `GetRegressionTargets(X)` returns `X.regression_ids` followed by targets of
  `regression_target` edges whose source is `X`, without duplicates.
- `GetLearningPath(A, B)` returns the shortest path from `A` to `B` following
  prerequisite edges in their direction (hard, plus soft unless
  `include_soft = false`). `A == B` returns `[A]`. An unreachable `B` is a
  success with `path_found = false` and an empty `path`.

### Optional booleans

`include_soft` uses proto3 `optional` so that "unset" can mean `true`. Clients
that want hard prerequisites only must set it to `false` explicitly.

### Pagination (`ListNodes`)

- Results are ordered by node id, so pages are deterministic for a version.
- `page_size`: `0` → 100, maximum 1000, negative → `CG_INVALID_REQUEST`.
- `page_token` is opaque and bound to the graph version and filters; a token
  from another version or filter set fails with `CG_INVALID_REQUEST`.
- `total_size` counts all matches across pages.

---

## Error model

Errors use standard gRPC status codes plus one `ErrorDetail` in the rich
status details (`grpc-status-details-bin`).

| Application error | gRPC status | `ErrorDetail.code` | Retryable |
|-------------------|-------------|--------------------|-----------|
| Node not found | `NOT_FOUND` | `CG_NODE_NOT_FOUND` | No |
| Profile not found | `NOT_FOUND` | `CG_PROFILE_NOT_FOUND` | No |
| Graph version mismatch | `FAILED_PRECONDITION` | `CG_INVALID_GRAPH_VERSION` | No |
| Graph not loaded / store unreachable | `UNAVAILABLE` | `CG_GRAPH_UNAVAILABLE` | Yes |
| Malformed or missing input | `INVALID_ARGUMENT` | `CG_INVALID_REQUEST` | No |

`ErrorDetail` fields: `code`, `message` (safe, no infrastructure details),
`request_id`, `graph_version` (per the invariant above).

---

## Compatibility rules (v1)

The package `aigora.curriculum_graph.v1` is the compatibility boundary.

### Allowed (additive)

- Add a new RPC to `CurriculumGraphService`.
- Add a new field with a new, never-used tag number.
- Add a new message or enum.
- Add a new enum value that consumers can safely treat as unknown.
- Mark a field or RPC `deprecated = true` (it stays available for all of v1).

### Forbidden (breaking — requires `v2`)

- Remove or rename an RPC, message, field, enum or enum value.
- Change a field's tag number, type or cardinality (`repeated`, `optional`).
- Change an RPC's request or response type.
- Reuse a tag number or name of a removed field (always `reserved` them).
- Change the documented meaning of an existing field.

### Examples

| Change | Verdict |
|--------|---------|
| Add `repeated string tags = 9;` to `Node` | Allowed |
| Add `rpc ListProfiles(...)` | Allowed |
| `string node_id = 2;` → `int64 node_id = 2;` | Forbidden |
| Remove `GetPrerequisites` | Forbidden |
| Renumber `Node.name` from 2 to 10 | Forbidden |

### Process

1. Edit the `.proto` (additive only).
2. Regenerate code and reference docs.
3. Run the compatibility gate against the committed contract lock.
4. Update the lock only for additive changes, in the same PR.

Breaking needs are collected for a future `aigora.curriculum_graph.v2`
package, served side by side with `v1` during migration.
