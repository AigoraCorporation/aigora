# Deterministic Orchestration Architecture

## Overview

This document defines the deterministic orchestration architecture used by the AIGORA Tutor Orchestrator.

The orchestration system coordinates:

- learning node retrieval
- candidate generation
- deterministic policy execution
- candidate ranking
- orchestration selection

while preserving:

- deterministic guarantees
- auditability
- bounded context isolation
- architectural governance
- decision traceability

The architecture is intentionally deterministic-first to ensure pedagogical consistency, reproducibility, and long-term maintainability.

---

# Architectural Principle

The Tutor Orchestrator acts as a deterministic pedagogical decision engine.

Each orchestration stage has a distinct responsibility:

| Stage | Responsibility |
|---|---|
| Retrieval | Defines what is reachable |
| Policies | Define what is allowed |
| Ranking | Defines what is preferred |
| Selection | Commits the final orchestration decision |

The orchestration pipeline evolves incrementally while preserving deterministic guarantees and explicit governance boundaries.

---

# High-Level Orchestration Pipeline

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

---

# Pipeline Responsibilities

| Stage | Responsibility | Owner | Deterministic Role | Output |
|---|---|---|---|---|
| Retrieval | Retrieve topology-valid learning nodes | Curriculum Graph | Determine reachability | Retrieved nodes |
| Candidate Generation | Build orchestration-ready candidates | Tutor Orchestrator | Build candidate space | CandidateNode set |
| Policy Filtering | Execute deterministic pedagogical policies | Tutor Orchestrator | Determine allowed candidates | Filtered candidates |
| Ranking | Apply deterministic scoring and ordering | Tutor Orchestrator | Determine candidate preference | Ranked candidates |
| Selection | Select the final learning node | Tutor Orchestrator | Commit orchestration decision | Selected node |

---

# Decision Engine

The deterministic decision engine is responsible for:

- policy execution
- ranking strategies
- tie-breaking strategies
- deterministic sequencing
- orchestration contracts
- bounded context enforcement
- deterministic selection guarantees

The decision engine must remain reproducible, auditable, and isolated from infrastructure-specific concerns.

---

# Policy Execution

The orchestration pipeline executes deterministic pedagogical policies such as:

- `EligibilityPolicy`
- `RegressionPolicy`
- `DifficultyPolicy`
- `CompletionPolicy`
- `ReviewPolicy`

Policy execution order must remain:

- deterministic
- reproducible
- stable
- traceable

No orchestration decision may bypass policy evaluation.

---

# Deterministic Guarantees

The orchestration architecture preserves the following guarantees:

- same input produces the same orchestration output
- deterministic traversal ordering
- deterministic policy execution
- deterministic ranking
- stable tie-breaking
- reproducible node selection
- graph version traceability
- explicit orchestration contracts
- deterministic orchestration sequencing

These guarantees are fundamental for pedagogical consistency and auditability.

---

# Event-Driven Pedagogical Flow

The orchestration lifecycle follows a deterministic event-driven flow:

```text
ExerciseCompleted
↓
MasteryEvaluated
↓
StudentModelUpdated
↓
PoliciesExecuted
↓
NodeSelected
```

This event sequence ensures that orchestration decisions are produced only after mastery evaluation and state synchronization are completed.

---

# Auditability and Decision Traceability

The orchestration system must support complete decision reconstruction.

The architecture preserves:

- policy execution tracing
- ranking trace reconstruction
- selection traceability
- graph version persistence
- candidate scoring traceability
- deterministic orchestration logs
- orchestration decision reproducibility

Every orchestration decision must be explainable and reconstructable.

---

# Interaction Boundaries

The architecture enforces strict interaction boundaries between components.

## Curriculum Graph

- The Tutor Orchestrator must never query Neo4j directly.
- Curriculum Graph owns curriculum topology and traversal behavior.
- Curriculum Graph must never perform pedagogical decisions.

## Tutor Orchestrator

- The Tutor Orchestrator owns orchestration coordination and pedagogical decision flow.
- All orchestration decisions must pass through deterministic policy evaluation.

## LLM Gateway

- LLM interactions must not bypass orchestration policies.
- LLM-generated content must remain governed by orchestration constraints.

## Student Interaction

- Student input must never mutate curriculum topology directly.
- Student-driven interactions must remain mediated through orchestration flows.

These boundaries preserve bounded context isolation and architectural governance.

---

# Architectural Constraints

The orchestration architecture intentionally separates:

| Responsibility | Owner |
|---|---|
| Curriculum topology | Curriculum Graph |
| Pedagogical orchestration | Tutor Orchestrator |
| Learning state | Student Model |
| Assessment and mastery evaluation | Assessment Engine |
| Content retrieval | Retrieval Layer |
| Language generation | LLM Gateway |

This separation prevents orchestration logic, curriculum ownership, and infrastructure concerns from becoming tightly coupled.

---

# Future Evolution

The current architecture is deterministic-first.

Future orchestration capabilities may introduce:

- heuristic-assisted ranking
- adaptive orchestration
- AI-assisted recommendation strategies
- probabilistic personalization
- experimentation layers
- hybrid orchestration pipelines

while preserving:

- deterministic governance guarantees
- orchestration auditability
- bounded context isolation
- architectural traceability
- pedagogical consistency

Deterministic orchestration establishes the governance foundation for future adaptive and AI-assisted orchestration evolution.