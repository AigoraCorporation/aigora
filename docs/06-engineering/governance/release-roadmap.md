# Release Roadmap

This document defines the planned evolution of AIGORA across versions.

It serves as the **single source of truth** for:

- upcoming releases
- current development focus
- component evolution

---

## Roadmap Overview

| Version | Name                                             | Planned Date | Status         | Primary Component  | Details                                                                   |
| ------- | ------------------------------------------------ | ------------ | -------------- | ------------------ | ------------------------------------------------------------------------- |
| v0.1.0  | Architecture Foundations                         | 2026-03-06   | ✅ Released    | Core               | [Release](https://github.com/AigoraCorporation/aigora/releases/tag/v0.1.0) |
| v0.1.1  | Architecture v1                                  | 2026-03-27   | ✅ Released    | Core               | [Release](https://github.com/AigoraCorporation/aigora/releases/tag/v0.1.1) |
| v0.2.0  | Curriculum Graph (Core Runtime)                  | 2026-04-24   | ✅ Released    | Curriculum Graph   | [Release](https://github.com/AigoraCorporation/aigora/issues/71)           |
| v0.2.1  | Curriculum Graph Persistence & Change Management | 2026-05-15   | ✅ Released    | Curriculum Graph   | [Release](https://github.com/AigoraCorporation/aigora/issues/124)          |
| v0.2.2  | Curriculum Graph API Foundation                  | 2026-09-18   | 🚧 In Progress | Curriculum Graph   | [Plan](https://github.com/AigoraCorporation/aigora/issues/186)             |
| v0.3.0  | Orchestrator Core (Deterministic)                | 2026-07-21   | ✅ Released | Tutor Orchestrator | [Release](https://github.com/AigoraCorporation/aigora/issues/185)             |
| v0.3.1  | Learning Session Orchestration                   | 2026-09-18   | 🚧 In Progress | Tutor Orchestrator | [Plan](https://github.com/AigoraCorporation/aigora/issues/253)             |
| v0.3.2  | Tutor Orchestrator gRPC Runtime                  | TBD          | ⏳ Planned     | Tutor Orchestrator | —                                                                        |
| v0.4.0  | Student Model Foundation                         | TBD          | ⏳ Planned     | Student Model      | —                                                                        |

---

## Current Release

### v0.2.2 — Curriculum Graph API Foundation

**Status:** 🚧 In Progress
**Primary Component:** Curriculum Graph

#### Scope

- Versioned, read-only gRPC API (v1 contracts, additive-only evolution)
- gRPC delivery adapter mapped to Curriculum Graph use cases
- Standardized error model and `graph_version` propagation
- Dockerized local runtime (API + Neo4j)
- Use case boundary enforcement
- Infrastructure isolation from delivery mechanisms

Out of scope: public REST API, graph write/publication operations.

Implementation plan: [v0.2.2 DAG](releases/v0.2.2-implementation-dag.md)

### v0.3.1 — Learning Session Orchestration

**Status:** 🚧 In Progress
**Primary Component:** Tutor Orchestrator

* Learning session lifecycle
* Session state management
* Exercise execution workflow
* Student progress tracking
* Assessment Engine integration
* Event-driven pedagogical flow
* Decision traceability and auditability

Implementation plan: [v0.3.1 plan](releases/v0.3.1-learning-session-orchestration-plan.md) ·
[v0.3.1 DAG](releases/v0.3.1-implementation-dag.md)

---

## Upcoming Releases

### v0.3.2 — Tutor Orchestrator gRPC Runtime

**Status:** ⏳ Planned
**Primary Component:** Tutor Orchestrator

#### Scope

- v1 protobuf contracts for the Tutor Orchestrator API
  (`SelectNextLearningNode`, `SelectRegressionNode`, `EvaluateLearningProgress`)
- Runnable gRPC server bootstrap mapped to application use cases
- Curriculum Graph gRPC adapter (consumes the v0.2.2 v1 contracts)
- Integration tests for the gRPC runtime boundary
- Student Model and Assessment ports wired to placeholder adapters until v0.4.0

Depends on: v0.2.2 (Curriculum Graph v1 gRPC contracts).

### v0.4.0 — Student Model Foundation

**Status:** ⏳ Planned
**Primary Component:** Student Model

#### Scope

- Student state representation
- Knowledge tracking
- Progress modeling
- Tutor Orchestrator Student Model and Assessment gRPC adapters
  (replacing the v0.3.2 placeholder adapters)

---

## Release Strategy

AIGORA follows a **component-driven release strategy**:

- Each release focuses on a primary component
- Cross-component integration happens incrementally
- Early versions prioritize architectural stability over feature completeness

---

## How to Update This Document

When a new release is created:

1. Move current release to "Released"
2. Update roadmap table
3. Promote next release to "Current"
4. Add a new future release if needed

---
