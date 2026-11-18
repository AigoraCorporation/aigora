# Curriculum Graph — Neo4j Publication

## Purpose

This document describes how Curriculum Graph snapshots are published to Neo4j.

Neo4j is treated as an infrastructure adapter. The application layer must interact with persistence through the `CurriculumGraphRepository` contract, not through Neo4j-specific classes.

---

## Publication Flow

```text
PublishGraphCommand
  ↓
PublishGraphUseCase
  ↓
LoadGraphUseCase
  ↓
CurriculumGraphRepository
  ↓
Neo4jCurriculumGraphRepository
  ↓
Neo4j
```

---

## Responsibility Split

| Component | Responsibility |
|---|---|
| `PublishGraphUseCase` | Orchestrates publication |
| `LoadGraphUseCase` | Loads and validates the graph snapshot |
| `CurriculumGraphRepository` | Defines the persistence contract |
| `Neo4jCurriculumGraphRepository` | Implements persistence using Neo4j |
| `CurriculumGraphPersistenceValidator` | Validates persisted state |

---

## Repository Boundary

The application layer must depend on:

```text
CurriculumGraphRepository
```

It must not depend on:

```text
Neo4jCurriculumGraphRepository
Neo4j driver
Cypher queries
Neo4j sessions
```

---

## Cypher Ownership

Cypher must remain inside infrastructure.

Allowed location:

```text
src/aigora/curriculum_graph/infrastructure/neo4j/
```

Forbidden locations:

```text
src/aigora/curriculum_graph/domain/
src/aigora/curriculum_graph/application/
```

---

## Persistence Validation

After publication, infrastructure may validate the persisted state.

Persistence validation is technical validation and belongs to infrastructure because it depends on Neo4j state.

---

## Published Snapshot (Read Model)

Since v0.2.2 publication is lossless and versioned, so the gRPC API can serve
exactly the published graph ([ADR-007](adr/ADR-007-read-only-grpc-api-foundation.md)).

| Element | Persisted properties |
|---------|----------------------|
| `(:Concept)` | `id`, `name`, `domain`, `description`, `mastery_criteria_json`, `error_taxonomy`, `prerequisite_ids`, `regression_ids`, `graph_version` |
| `-[:PREREQUISITE_OF]->` | `type` (part of the MERGE key, so a hard and a regression edge between the same concepts stay distinct), `graph_version` |
| `(:CurriculumProfile)` | `id`, `name`, `required_nodes`, `mastery_targets_json`, `node_weights_json`, `progression_path`, `exam_skill_overlay`, `graph_version` |
| `(:GraphMetadata {key: 'active'})` | `graph_version`, `node_count`, `edge_count`, `profile_count`, `published_at` |

The `:GraphMetadata` node marks the active version. `Neo4jCurriculumGraphReader`
(the `CurriculumGraphReader` port adapter) loads only elements stamped with
that version, so leftovers from earlier publications are ignored.

Graphs published before v0.2.2 lack these properties; the reader reports them
as unavailable until they are republished.

---

## Constraints

- Publication must go through `PublishGraphUseCase`.
- Persistence must go through `CurriculumGraphRepository`.
- Neo4j implementation details must stay in infrastructure.
- Graph loading must remain file-based and deterministic.
- Student mastery state must not be stored in the Curriculum Graph persistence model.

---

## Summary

Neo4j publication is an infrastructure concern orchestrated by the application use case through a domain repository contract.
