# Decision Engine Design

## Overview

This document defines the Decision Engine architecture used by the AIGORA Tutor Orchestrator.

The Decision Engine acts as the deterministic pedagogical reasoning core responsible for:

- orchestration coordination
- policy execution
- candidate evaluation
- deterministic ranking
- tie-breaking
- final learning node selection

The architecture is intentionally deterministic-first and designed to evolve incrementally while preserving:

- deterministic behavior
- orchestration traceability
- bounded context isolation
- auditability
- reproducible pedagogical decisions

---

# Architectural Principle

The Decision Engine coordinates orchestration stages using:

- explicit orchestration policies
- deterministic evaluation strategies
- ranking rules
- stable tie-breaking
- reproducible selection guarantees

The orchestration architecture must preserve deterministic governance across all orchestration stages.

Every orchestration decision must remain explainable, traceable, and reproducible.

---

# Decision Engine Responsibilities

| Responsibility | Purpose | Deterministic Role | Primary Output |
|---|---|---|---|
| Orchestration Coordination | Coordinate orchestration stages | Ensure deterministic orchestration flow | Orchestration pipeline execution |
| Policy Execution | Evaluate pedagogical constraints | Determine allowed candidates | Filtered candidates |
| Ranking Evaluation | Score and prioritize candidates | Determine candidate preference | Ranked candidates |
| Selection | Choose the final learning node | Commit final orchestration decision | Selected node |
| Tie-Breaking | Resolve equivalent candidates | Guarantee deterministic ordering | Stable orchestration output |
| Auditability | Trace orchestration decisions | Preserve reproducibility | Decision trace |

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

# Orchestration Engine

The orchestration engine coordinates execution flow between orchestration stages.

## Responsibilities

- pipeline coordination
- orchestration stage sequencing
- candidate lifecycle management
- deterministic execution ordering
- bounded context coordination
- orchestration flow management

The orchestration engine guarantees that all orchestration stages execute in a stable and reproducible order.

---

# Policy Engine

The policy engine evaluates deterministic pedagogical constraints using explicit orchestration policies.

## Policies

- `EligibilityPolicy`
- `RegressionPolicy`
- `DifficultyPolicy`
- `CompletionPolicy`
- `ReviewPolicy`

## Responsibilities

- candidate validation
- progression restriction
- remediation enforcement
- deterministic orchestration filtering
- pedagogical governance enforcement

Policy execution order must remain:

- deterministic
- reproducible
- traceable
- stable

No orchestration stage may bypass policy evaluation.

---

# Strategy Engine

The strategy engine defines how orchestration candidates are evaluated, prioritized, and selected.

## Responsibilities

- ranking strategies
- selection strategies
- tie-breaking strategies
- fallback strategies
- weighting strategies
- deterministic scoring

The strategy engine transforms policy-approved candidates into stable orchestration preference ordering.

---

# Ranking and Selection

Ranking and selection have distinct orchestration responsibilities.

| Stage | Responsibility |
|---|---|
| Ranking | Creates candidate preference ordering |
| Selection | Commits the final orchestration decision |

## Ranking Responsibilities

- candidate scoring
- weighted prioritization
- deterministic ordering
- stable candidate evaluation

## Selection Responsibilities

- stable tie-breaking
- deterministic fallback selection
- orchestration commitment
- reproducible node selection

Ranking evaluates preference.

Selection commits the final pedagogical decision.

This separation preserves orchestration clarity and bounded governance.

---

# Deterministic Evaluation

The Decision Engine preserves the following deterministic guarantees:

- same input produces the same orchestration output
- deterministic policy execution
- deterministic ranking
- stable orchestration ordering
- deterministic tie-breaking
- graph version traceability
- reproducible selection guarantees
- deterministic orchestration sequencing

These guarantees ensure orchestration consistency and pedagogical reproducibility.

---

# Orchestration Contracts

The Decision Engine enforces explicit orchestration contracts between components.

| Component | Responsibility |
|---|---|
| Curriculum Graph | Owns topology retrieval |
| Tutor Orchestrator | Owns pedagogical orchestration decisions |
| Policy Engine | Owns candidate validation and pedagogical constraints |
| Strategy Engine | Owns ranking and prioritization behavior |
| Selection Layer | Owns final orchestration commitment |

## Governance Constraints

- policies cannot mutate curriculum topology
- ranking cannot bypass policy execution
- selection cannot bypass deterministic guarantees
- orchestration stages must remain auditable
- orchestration logic must remain isolated from infrastructure concerns

These constraints preserve architectural governance and bounded context isolation.

---

# Auditability and Traceability

The orchestration architecture must support complete decision reconstruction.

The Decision Engine preserves:

- policy execution tracing
- candidate evaluation traceability
- ranking trace reconstruction
- selection traceability
- graph version persistence
- orchestration reproducibility
- deterministic orchestration logs

Every orchestration decision must remain explainable and reconstructable.

---

# Event-Driven Coordination

The orchestration lifecycle follows a deterministic event-driven flow.

```text
ExerciseCompleted
↓
AssessmentEvaluated
↓
StudentModelUpdated
↓
PoliciesExecuted
↓
CandidateRanked
↓
NodeSelected
```

This sequencing guarantees that orchestration decisions occur only after assessment evaluation and student state synchronization are completed.

---

# Architectural Constraints

The Decision Engine enforces strict orchestration boundaries.

| Constraint | Description |
|---|---|
| Curriculum Graph isolation | Curriculum Graph does not perform pedagogical decisions |
| Policy isolation | Policies cannot directly mutate graph topology |
| Ranking isolation | Ranking cannot commit orchestration decisions |
| Selection isolation | Selection must preserve deterministic guarantees |
| Infrastructure isolation | Decision logic remains independent from infrastructure concerns |

These constraints preserve orchestration governance and architectural consistency.

---

# Future Evolution

The current Decision Engine architecture is deterministic-first.

Future orchestration capabilities may progressively introduce:

- heuristic-assisted orchestration
- adaptive ranking
- AI-assisted recommendation strategies
- semantic evaluation layers
- probabilistic prioritization
- hybrid orchestration strategies

while preserving:

- deterministic governance guarantees
- orchestration auditability
- bounded context isolation
- architectural traceability
- pedagogical consistency

The deterministic Decision Engine establishes the governance foundation for future adaptive orchestration evolution.