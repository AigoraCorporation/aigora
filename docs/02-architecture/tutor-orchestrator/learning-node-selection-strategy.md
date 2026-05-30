# AIGORA — Learning Node Selection Strategy

## Overview

This document defines the learning node selection architecture used by the AIGORA Tutor Orchestrator.

The selection system is responsible for determining the final learning node after orchestration evaluation, policy execution, and candidate ranking are completed.

The architecture is intentionally deterministic-first and evolves incrementally toward student-aware and adaptive orchestration capabilities.

Selection operates as the final orchestration commitment layer.

---

# Selection Architecture

The selection pipeline operates after candidate ranking has already produced an ordered candidate set.

```text
retrieval
↓
candidate generation
↓
policy filtering
↓
ranking
↓
selection
```

Ranking determines candidate preference ordering.

Selection commits the final orchestration decision.

---

# Selection Categories

The orchestration engine organizes selection behavior into distinct categories according to orchestration maturity and dependency scope.

---

# 1. Graph-Only Selection

Graph-only selection strategies depend exclusively on curriculum topology and deterministic ranking output.

These strategies do not require Student Model integration.

## Responsibilities

- highest-ranked topology-valid node selection
- deterministic tie-breaking
- stable deterministic ordering
- traversal-priority selection
- deterministic fallback selection
- adjacency-preserving progression

## Example Rules

- highest-ranked topology-valid node wins
- fallback to nearest adjacent node
- preserve deterministic traversal ordering
- prefer nodes with lower dependency distance

## Example

```text
If two nodes have the same score,
select the node with the lowest dependency distance.
```

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

Graph-only selection establishes the deterministic foundation of orchestration commitment behavior.

---

# 2. Student-Aware Selection

Student-aware selection strategies depend on student learning state and pedagogical progression signals.

These strategies require Student Model integration.

## Responsibilities

- remediation overrides
- review-first selection
- unstable mastery prioritization
- regression-triggered selection
- learning fatigue avoidance
- progression pacing control

## Example Rules

- prefer remediation over progression when mastery instability is detected
- prioritize review nodes after repeated mistakes
- avoid progression during unstable learning periods

## Example

```text
Select remediation instead of progression
when mastery instability is detected.
```

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

Student-aware selection introduces personalized orchestration behavior while preserving deterministic governance guarantees.

---

# 3. Hybrid Selection

Hybrid selection combines curriculum topology with adaptive student-aware orchestration behavior.

These strategies represent advanced orchestration capabilities.

## Responsibilities

- personalized progression selection
- adaptive learning path overrides
- context-aware remediation
- dynamic progression balancing
- heuristic-assisted deterministic selection
- adaptive pedagogical prioritization

## Example Rules

- dynamically rebalance progression and remediation
- adapt progression pacing to learning stability
- prioritize topology-valid nodes with the highest pedagogical value

## Example

```text
Select the topology-valid node with the highest
pedagogical progression value for the current student context.
```

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

Hybrid selection represents the long-term evolution of adaptive pedagogical orchestration within AIGORA.

---

# Deterministic Guarantees

The selection architecture preserves the following guarantees:

- same input produces the same selection result
- stable deterministic tie-breaking
- reproducible orchestration decisions
- deterministic fallback selection
- explicit override rules
- deterministic orchestration sequencing
- auditable decision traceability

These guarantees ensure pedagogical consistency and orchestration reproducibility.

---

# Selection vs Ranking

Selection and ranking have different responsibilities inside the orchestration pipeline.

| Stage | Responsibility |
|---|---|
| Ranking | Creates candidate preference ordering |
| Selection | Creates the final orchestration commitment |

Ranking evaluates preference.

Selection commits the final pedagogical decision.

This separation preserves orchestration clarity, deterministic governance, and auditability.

---

# Architectural Principle

The selection architecture evolves incrementally while preserving deterministic guarantees.

Initial implementations prioritize:

- topology consistency
- deterministic ordering
- stable tie-breaking
- reproducible orchestration commitments

Future orchestration capabilities may progressively introduce:

- adaptive progression balancing
- heuristic-assisted prioritization
- personalized orchestration behavior
- dynamic remediation strategies

while preserving:

- deterministic governance guarantees
- orchestration auditability
- bounded context isolation
- pedagogical consistency

---

# Governance Constraints

The selection system must preserve the following architectural constraints:

- selection must always occur after policy evaluation
- ranking must not directly commit orchestration decisions
- all selection overrides must remain explicit and traceable
- student state must not bypass deterministic governance rules
- topology ownership remains isolated inside Curriculum Graph
- heuristic orchestration must not violate deterministic guarantees

These constraints preserve long-term orchestration consistency as adaptive capabilities evolve.