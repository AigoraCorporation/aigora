# ADR-004 — Event-Driven Pedagogical Flow

## Status

Accepted

## Context

The Tutor Orchestrator must coordinate learning progression across multiple pedagogical stages.

A purely synchronous or implicit orchestration flow would:

- make decision reconstruction harder
- reduce observability
- hide important learning state transitions
- make orchestration behavior harder to audit
- complicate future asynchronous orchestration
- increase coupling between assessment, student state, and node selection

The architecture requires an explicit way to represent pedagogical progression events and preserve traceability across the orchestration lifecycle.

## Decision

The Tutor Orchestrator must model pedagogical progression as an explicit event-driven flow.

The orchestration lifecycle must be represented through explicit educational events such as:

- ExerciseCompleted
- AssessmentEvaluated
- MasteryEvaluated
- StudentModelUpdated
- PoliciesExecuted
- CandidateRanked
- NodeSelected

These events must preserve the order and traceability of the pedagogical orchestration process.

The event-driven flow must:

- make orchestration stages explicit
- preserve decision traceability
- support auditability
- enable future asynchronous orchestration
- support event reconstruction
- preserve deterministic sequencing

The event-driven flow must not:

- bypass deterministic policy evaluation
- allow events to mutate curriculum topology directly
- allow LLM output to trigger progression without orchestration governance
- hide orchestration state transitions
- replace the deterministic decision engine

## Consequences

### Positive

- clearer orchestration lifecycle
- improved observability
- better auditability
- easier decision reconstruction
- stronger pedagogical traceability
- better foundation for future async orchestration
- improved separation between stages

### Negative

- additional event modeling effort
- more documentation required
- future need for event versioning
- possible increase in implementation complexity

## Constraints

- event sequencing must remain deterministic
- orchestration events must be traceable
- event payloads must support decision reconstruction
- curriculum topology must not be mutated by orchestration events
- policy execution must remain mandatory before node selection
- event-driven flow must preserve deterministic governance