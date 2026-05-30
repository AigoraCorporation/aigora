# Event-Driven Pedagogical Flow

## Overview

This document defines the event-driven pedagogical orchestration flow used by the AIGORA Tutor Orchestrator.

The architecture coordinates assessment, orchestration, student progression, and deterministic learning node selection through explicit educational events.

The orchestration lifecycle is intentionally event-driven to preserve:

- deterministic sequencing
- auditability
- bounded context isolation
- orchestration traceability
- reproducible pedagogical decisions

---

# Architectural Principle

Pedagogical orchestration must evolve through explicit, traceable, and reproducible educational events.

Events coordinate orchestration stages while preserving deterministic orchestration guarantees and architectural governance boundaries.

The event flow acts as the synchronization mechanism between learning progression, assessment evaluation, student state mutation, and orchestration decisions.

---

# High-Level Event Flow

```text
ExerciseCompleted
↓
AssessmentEvaluated
↓
MasteryEvaluated
↓
StudentModelUpdated
↓
PoliciesExecuted
↓
CandidateRanked
↓
NodeSelected
```

---

# Event Responsibilities

| Event | Purpose | Owner | Output |
|---|---|---|---|
| `ExerciseCompleted` | Capture exercise completion and student interaction outcome | Tutor Orchestrator | Exercise submission |
| `AssessmentEvaluated` | Evaluate answer quality and correctness | Assessment Engine | Assessment result |
| `MasteryEvaluated` | Determine mastery progression and learning state impact | Tutor Orchestrator | Mastery decision |
| `StudentModelUpdated` | Persist updated learning state and progression data | Student Model | Updated student state |
| `PoliciesExecuted` | Execute deterministic pedagogical policies | Tutor Orchestrator | Filtered candidates |
| `CandidateRanked` | Rank orchestration candidates deterministically | Tutor Orchestrator | Ranked candidates |
| `NodeSelected` | Commit the next pedagogical orchestration decision | Tutor Orchestrator | Selected learning node |

---

# Orchestration Lifecycle

The orchestration lifecycle follows a deterministic progression model.

## 1. Exercise Completion

The student completes a learning interaction.

The orchestration layer captures:

- exercise submission
- interaction metadata
- timing information
- learning context

This event initiates the pedagogical orchestration flow.

---

## 2. Assessment Evaluation

The Assessment Engine evaluates:

- correctness
- answer quality
- conceptual understanding
- learning performance indicators

Assessment results become orchestration signals for mastery evaluation.

---

## 3. Mastery Evaluation

The orchestration layer determines:

- mastery progression
- instability signals
- regression indicators
- remediation requirements

This stage transforms assessment outcomes into pedagogical state decisions.

---

## 4. Student State Synchronization

The Student Model persists:

- updated mastery levels
- progression history
- learning gaps
- remediation state
- interaction evidence

This stage guarantees orchestration consistency before future decisions occur.

---

## 5. Policy Execution

The Tutor Orchestrator executes deterministic orchestration policies such as:

- eligibility validation
- progression constraints
- regression policies
- review prioritization
- remediation enforcement

Only policy-approved candidates may continue to ranking.

---

## 6. Candidate Ranking

The orchestration engine applies deterministic ranking strategies to produce a stable candidate ordering.

Ranking may include:

- topology priority
- remediation priority
- progression stability
- deterministic tie-breaking

Ranking produces preference ordering but does not commit the final orchestration decision.

---

## 7. Node Selection

The selection layer commits the final pedagogical orchestration decision.

The selected node becomes:

- the next learning objective
- the next guided learning session
- the next pedagogical interaction target

Selection must remain deterministic, reproducible, and auditable.

---

# Observability and Traceability

The orchestration architecture must preserve complete event traceability.

The system supports:

- event sequencing traceability
- pedagogical event reconstruction
- asynchronous orchestration visibility
- deterministic orchestration logs
- policy execution tracing
- ranking traceability
- selection traceability
- orchestration reproducibility

Every orchestration decision must be reconstructable through event history.

---

# Deterministic Guarantees

The event-driven orchestration flow preserves the following guarantees:

- stable event sequencing
- reproducible orchestration flow
- deterministic policy execution
- deterministic ranking
- deterministic node selection
- explicit orchestration sequencing
- stable decision reconstruction

The same orchestration inputs must always produce the same orchestration outputs.

---

# Architectural Constraints

The event-driven orchestration model enforces strict architectural boundaries.

| Constraint | Description |
|---|---|
| Curriculum Graph isolation | Curriculum Graph does not perform pedagogical decisions |
| Deterministic governance | All orchestration decisions must pass through deterministic policy evaluation |
| Student state ownership | Student state mutation belongs exclusively to orchestration and assessment flows |
| Selection isolation | Ranking does not directly commit orchestration decisions |
| Event sequencing integrity | Events must preserve deterministic ordering |

These constraints preserve bounded context isolation and orchestration governance consistency.

---

# Future Evolution

The current orchestration architecture is deterministic-first.

Future orchestration capabilities may progressively introduce:

- distributed event streaming
- asynchronous orchestration pipelines
- heuristic-assisted orchestration
- adaptive pedagogical event processing
- event-driven personalization
- hybrid orchestration coordination

while preserving:

- deterministic governance guarantees
- orchestration auditability
- architectural traceability
- bounded context isolation
- pedagogical consistency

The event-driven model establishes the orchestration foundation for future distributed and adaptive learning systems.