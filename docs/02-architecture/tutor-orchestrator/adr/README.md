# Architecture Decision Records

**Last Updated**: 2026-06-04

This directory contains Architecture Decision Records (ADRs) documenting significant architectural and technical decisions for the Tutor Orchestrator component.

Use the shared ADR template at [`docs/06-engineering/governance/templates/ADR-TEMPLATE.md`](../../../06-engineering/governance/templates/ADR-TEMPLATE.md) when creating new records.

---

## ✅ Accepted (Implemented)

| ADR                                                         | Title                                 | Version | Date       |
| ----------------------------------------------------------- | ------------------------------------- | ------- | ---------- |
| [ADR-001](../adr/ADR-001-deterministic-first-orchestration.md)     | Deterministic-First Orchestration     | v0.1.0  | 2026-06-04 |
| [ADR-002](../adr/ADR-002-curriculum-graph-integration-via-grpc.md) | Curriculum Graph Integration via gRPC | v0.1.0  | 2026-06-04 |
| [ADR-003](../adr/ADR-003-decision-engine-decomposition.md)         | Decision Engine Decomposition         | v0.1.0  | 2026-06-04 |
| [ADR-004](../adr/ADR-004-event-driven-pedagogical-flow.md)         | Event-Driven Pedagogical Flow         | v0.1.0  | 2026-06-04 |
| [ADR-005](../adr/ADR-005-auditability-first-architecture.md)       | Auditability-First Architecture       | v0.1.0  | 2026-06-04 |

---

## 📖 Reading Order

New contributors should read ADRs in the following order:

1. ADR-001 — Deterministic-First Orchestration
2. ADR-002 — Curriculum Graph Integration via gRPC
3. ADR-003 — Decision Engine Decomposition
4. ADR-004 — Event-Driven Pedagogical Flow
5. ADR-005 — Auditability-First Architecture

This sequence follows the evolution of the Tutor Orchestrator architecture, from foundational orchestration principles to execution flow and governance concerns.

---

## Scope

The ADRs in this directory document decisions related to:

* pedagogical orchestration
* deterministic decision-making
* orchestration engine decomposition
* integration boundaries
* service contracts
* auditability
* traceability
* governance
* runtime architecture

Infrastructure decisions owned by other components should be documented within their respective ADR directories.

---

## Ownership

The Tutor Orchestrator ADRs are responsible for documenting decisions related to:

* pedagogical decision-making
* orchestration architecture
* orchestration governance
* engine responsibilities
* component boundaries
* integration contracts

Curriculum topology, graph persistence, and graph infrastructure decisions remain owned by the Curriculum Graph ADRs.

---
