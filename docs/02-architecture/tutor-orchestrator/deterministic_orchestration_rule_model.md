# Deterministic Orchestration Rule Model

## Overview

This document defines the rule categories used by the AIGORA Tutor Orchestrator and describes how deterministic orchestration policies evolve over time.

The orchestration architecture is intentionally incremental.

The system starts with topology-driven deterministic orchestration and progressively evolves toward student-aware and hybrid pedagogical orchestration as the platform matures.

---

# Rule Categories

The orchestration engine organizes rules into distinct categories according to the information required for evaluation.

---

# 1. Graph-Only Rules

Graph-only rules depend exclusively on curriculum topology and graph structure.

These rules operate without requiring student-specific learning state.

## Responsibilities

- adjacency validation
- prerequisite existence validation
- graph traversal constraints
- archived node filtering
- traversal depth limits
- topology consistency validation

## Characteristics

| Property | Description |
|---|---|
| Dependency Scope | Curriculum Graph only |
| Student State Dependency | No |
| Determinism Level | Fully deterministic |
| Execution Complexity | Low |
| Initial Adoption Priority | Highest |

## Status

```text
IMPLEMENTED FIRST
```

Graph-only rules establish the deterministic foundation of the orchestration pipeline.

---

# 2. Student-Aware Rules

Student-aware rules depend on student learning state and mastery progression signals.

These rules introduce personalized orchestration behavior while preserving deterministic governance.

## Responsibilities

- prerequisite mastery thresholds
- already-mastered node filtering
- review prioritization
- regression eligibility
- recent mistake analysis
- cooldown period enforcement
- mastery progression validation

## Characteristics

| Property | Description |
|---|---|
| Dependency Scope | Student Model |
| Student State Dependency | Yes |
| Determinism Level | Deterministic |
| Execution Complexity | Medium |
| Initial Adoption Priority | Incremental |

## Status

```text
PLANNED FOR FUTURE ITERATIONS
```

Student-aware rules become progressively more important as the Student Model matures and accumulates reliable learning signals.

---

# 3. Hybrid Rules

Hybrid rules combine curriculum topology with student learning state.

These rules enable advanced adaptive orchestration behavior while preserving bounded governance constraints.

## Responsibilities

- topology-valid but pedagogically blocked nodes
- adaptive progression constraints
- dynamic remediation paths
- personalized learning progression
- context-aware candidate prioritization
- adaptive review orchestration

## Characteristics

| Property | Description |
|---|---|
| Dependency Scope | Curriculum Graph + Student Model |
| Student State Dependency | Yes |
| Determinism Level | Hybrid deterministic orchestration |
| Execution Complexity | High |
| Initial Adoption Priority | Advanced orchestration phase |

## Status

```text
PLANNED FOR ADVANCED ORCHESTRATION
```

Hybrid rules represent the long-term evolution of pedagogical orchestration within AIGORA.

---

# Rule Evolution Strategy

The orchestration architecture evolves incrementally across multiple maturity stages.

```text
Graph-Only Rules
↓
Student-Aware Rules
↓
Hybrid Rules
```

This progression allows the platform to:

- establish deterministic guarantees early
- preserve orchestration auditability
- progressively introduce personalization
- avoid premature orchestration complexity
- maintain bounded context isolation

---

# Architectural Principle

The orchestration pipeline is deterministic-first.

Initial implementations prioritize:

- topology consistency
- deterministic traversal
- explicit orchestration contracts
- reproducible decision-making

As the Student Model evolves, the orchestration engine progressively introduces:

- adaptive progression
- remediation strategies
- personalized ranking
- hybrid orchestration behavior

while preserving:

- deterministic governance guarantees
- orchestration traceability
- bounded context isolation
- pedagogical consistency

---

# Governance Constraints

The orchestration rule system must preserve the following constraints:

- all orchestration decisions must remain explainable
- orchestration policies must remain reproducible
- student state must never bypass deterministic policy evaluation
- curriculum topology ownership remains isolated inside Curriculum Graph
- orchestration rules must remain independent from infrastructure concerns
- heuristic orchestration must not violate deterministic governance guarantees

These constraints ensure long-term architectural consistency as orchestration complexity evolves.