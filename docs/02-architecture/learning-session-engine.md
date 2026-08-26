# Learning Session Engine

## v0.3.1 deployment decision

For v0.3.1, Learning Session is a **logical ownership boundary inside the existing `tutor-orchestrator` Maven module and deployable**. It is not introduced as a separate service and it does not introduce a new `learningsession` package root.

The implementation is deliberately placed in the package structure that already exists under `com.aigora.tutororchestrator`:

- `domain/model` — `LearningSession`, `ExerciseAttempt`, lifecycle states, session events;
- `domain/valueobjects` — session-specific identifiers and versions not already present;
- `domain/policy` — session continuation and completion policies;
- `application/contracts/command` — session commands;
- `application/contracts/result` — typed session results;
- `application/ports` — repository, assessment, event, trace, telemetry and Tutor Orchestrator boundaries;
- `application/usecase` — start, exercise completion, progress processing and recovery coordination;
- `infrastructure` — in-memory adapters required by the v0.3.1 release plan;
- `adapters/outbound` — in-process bridge to the deterministic Tutor Orchestrator pipeline.

This physical co-location does **not** change the ownership rules of ADR-008: Learning Session lifecycle state is mutated only through the Learning Session aggregate/use cases, while candidate generation, policy evaluation, ranking and node selection remain responsibilities of the Tutor Orchestrator decision flow.

A future ADR may extract the Learning Session ownership boundary into a separate module or deployable if scale, durability or operational isolation requires it. v0.3.1 does not make that extraction.
