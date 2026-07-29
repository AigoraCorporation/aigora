# ADR-010 — Event Publication and Consistency Boundaries

- **Status:** Accepted
- **Date:** 2026-07-29
- **Decision Owners:** AIGORA Architecture
- **Milestone:** v0.3.1 — Learning Session Orchestration
- **Supersedes:** None
- **Superseded by:** None
- **Related ADRs:**
  - ADR-001 — Deterministic-First Orchestration
  - ADR-003 — Decision Engine Decomposition
  - ADR-004 — Event-Driven Pedagogical Flow
  - ADR-005 — Auditability-First Architecture
  - ADR-008 — Learning Session Ownership and Bounded-Context Boundaries
  - ADR-009 — Learning Session Aggregate and Lifecycle Model

---

# 1. Context

The AIGORA platform is composed of multiple bounded contexts that collaborate to execute an adaptive learning experience.

Examples include:

- Learning Session Engine
- Tutor Orchestrator
- Assessment Engine
- Student Model
- Curriculum Graph
- Retrieval Layer
- LLM Gateway

Each component owns its own business responsibilities and persistence boundaries.

As the platform evolves, components increasingly communicate through events instead of direct synchronous interactions.

Without a well-defined event architecture, several architectural risks emerge:

- duplicated event publication;
- inconsistent ordering;
- non-reproducible decisions;
- event loss;
- duplicated event consumption;
- distributed race conditions;
- hidden coupling between bounded contexts;
- non-idempotent consumers;
- inability to reconstruct historical decisions;
- incompatible event evolution over time.

Since one of the long-term goals of AIGORA is to support:

- asynchronous orchestration;
- distributed execution;
- auditability;
- observability;
- replayable decisions;
- scalable orchestration;

event publication must become a first-class architectural concern.

---

# 2. Problem Statement

Multiple bounded contexts produce business facts.

Examples include:

Learning Session Engine

- Exercise completed
- Session completed
- Session interrupted

Assessment Engine

- Assessment finished
- Assessment accepted

Tutor Orchestrator

- Candidate ranking completed
- Policies executed
- Next node selected

Student Model

- Student model updated

Curriculum Graph

- Graph version changed

Without architectural rules, every component could publish events differently.

Examples:

- different event identifiers
- incompatible timestamps
- incompatible schemas
- different ordering semantics
- inconsistent retries
- inconsistent versioning
- inconsistent correlation identifiers

This would make distributed debugging extremely difficult.

---

# 3. Decision

AIGORA adopts an **Event-First Architecture** for communication between bounded contexts.

Every business fact that may be consumed outside its owning bounded context shall be represented by an explicit event.

Events become part of the public architectural contract.

Each event must:

- have exactly one authoritative publisher;
- have one semantic meaning;
- represent a committed business fact;
- never represent an intention;
- never represent an intermediate state;
- be immutable;
- be versioned;
- be replayable;
- be traceable.

---

# 4. Architectural Principles

The following principles govern every event published inside AIGORA.

## Principle 1 — Events represent facts

Events describe something that has already happened.

Correct:

- ExerciseCompleted
- AssessmentAccepted
- LearningSessionCompleted

Incorrect:

- CompleteExercise
- UpdateStudentModel
- EvaluateAssessment

Commands request work.

Events describe completed work.

---

## Principle 2 — Events are immutable

Published events shall never be modified.

If business meaning changes, a new event version must be introduced.

Consumers must treat historical events as immutable records.

---

## Principle 3 — Single publisher

Every event has exactly one owner.

Example:

LearningSessionCompleted

Publisher:

Learning Session Engine

Never:

Tutor Orchestrator

Assessment Engine

Student Model

Only one bounded context owns the fact represented by the event.

---

## Principle 4 — Publication occurs after successful state transition

An event shall only be published after:

1. aggregate validation;
2. successful mutation;
3. persistence;
4. successful transaction completion.

Publishing events before persistence is prohibited.

---

## Principle 5 — Events are append-only

Previously published events are historical records.

Events are never deleted.

Consumers reconstruct history through ordered event sequences.

---

## Principle 6 — Events are integration contracts

Events are part of the public architecture.

Breaking changes require explicit versioning.

---

# 5. Event Categories

AIGORA distinguishes three different categories of events.

## 5.1 Domain Events

Represent changes inside one bounded context.

Characteristics:

- business meaning;
- aggregate scoped;
- immutable;
- owned by one bounded context.

Examples:

LearningSessionCreated

ExerciseCompleted

LearningSessionCompleted

AssessmentAccepted

StudentModelUpdated

---

## 5.2 Application Events

Represent orchestration steps internal to an application layer.

These events coordinate internal workflows.

They are implementation details.

Examples:

AssessmentRequested

DecisionRequested

DecisionApplied

CacheInvalidated

Application Events should not be exposed as long-term integration contracts.

---

## 5.3 Integration Events

Represent communication between bounded contexts.

Examples:

LearningSessionCompleted

↓

Student Model

↓

Analytics

↓

Audit subsystem

↓

Notification subsystem

↓

Observability subsystem

Integration Events require:

- stable schema;
- explicit version;
- backward compatibility;
- replay support.

---

# 6. Event Ownership

Every event belongs to exactly one bounded context.

Ownership determines:

- publisher;
- schema authority;
- semantic authority;
- version authority.

Consumers never redefine event semantics.

---

## 6.1 Learning Session Engine

Owns:

- LearningSessionCreated
- LearningSessionStarted
- ExercisePresented
- ExerciseCompleted
- LearningSessionCompleted
- LearningSessionInterrupted
- LearningSessionFailed

---

## 6.2 Assessment Engine

Owns:

- AssessmentRequested
- AssessmentCompleted
- AssessmentAccepted
- AssessmentRejected

---

## 6.3 Tutor Orchestrator

Owns:

- CandidatesGenerated
- CandidatesRanked
- PoliciesExecuted
- NodeSelected
- CompletionSelected
- RegressionSelected

---

## 6.4 Student Model

Owns:

- StudentModelUpdated
- MasteryUpdated
- ConfidenceUpdated

---

## 6.5 Curriculum Graph

Owns:

- CurriculumGraphPublished
- CurriculumGraphVersionChanged

---

## 6.6 Retrieval Layer

Owns:

- RetrievalCompleted

---

## 6.7 LLM Gateway

Owns:

- GenerationCompleted
- GenerationFailed

---

# 7. Event Naming Convention

Events follow the pattern:

<Entity><PastTenseVerb>

Examples:

ExerciseCompleted

LearningSessionStarted

AssessmentAccepted

StudentModelUpdated

NodeSelected

Incorrect examples:

CompleteExercise

Assessment

Node

DoWork

Every event name must communicate a completed business fact.

---

# 8. Publication Lifecycle

Every event follows the same lifecycle.

```text
Business Command

↓

Aggregate Validation

↓

Aggregate Mutation

↓

Persistence

↓

Transaction Commit

↓

Event Creation

↓

Event Publication

↓

Consumer Processing
```

Publication before persistence is forbidden.

---

# 9. Publication Guarantees

AIGORA guarantees:

- events represent committed facts;
- event ordering inside one aggregate;
- immutable payloads;
- explicit ownership;
- deterministic publication sequence;
- versioned schemas;
- replay capability;
- audit traceability.

Global ordering across multiple aggregates is **not guaranteed**.
