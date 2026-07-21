# ADR-001 — Deterministic-First Orchestration

## Status

Accepted

## Context

The Tutor Orchestrator is responsible for making pedagogical decisions that directly influence student progression.

Introducing heuristic, probabilistic, or AI-driven decision-making as the initial orchestration model would:

* reduce predictability
* increase operational complexity
* make testing more difficult
* reduce decision explainability
* complicate auditability
* make orchestration outcomes harder to reproduce

The first version of the Tutor Orchestrator requires a deterministic and governable foundation that allows orchestration decisions to be explained, reconstructed, and validated.

## Decision

The Tutor Orchestrator must follow a deterministic-first orchestration architecture.

All orchestration decisions must be produced through explicit and reproducible orchestration stages.

The orchestration pipeline must:

* generate candidates deterministically
* evaluate candidates through explicit policies
* rank candidates using deterministic strategies
* select learning nodes through deterministic selection rules
* preserve decision traceability
* support orchestration reproducibility

The orchestration architecture must be composed of specialized engines responsible for:

* orchestration coordination
* policy evaluation
* candidate ranking
* learning node selection
* decision traceability

The initial implementation must not:

* depend on LLM-generated decisions
* use probabilistic ranking
* use non-deterministic candidate selection
* allow runtime randomness to influence decisions
* bypass policy evaluation
* bypass auditability requirements

## Consequences

### Positive

* deterministic behavior
* reproducible orchestration decisions
* easier testing
* simpler debugging
* explicit governance model
* improved auditability
* decision traceability
* clear separation of responsibilities
* stable foundation for future evolution

### Negative

* lower short-term adaptability
* limited personalization in early iterations
* additional effort required to define explicit policies
* slower introduction of adaptive orchestration capabilities

## Constraints

* orchestration decisions must be reproducible
* policy execution must be deterministic
* ranking must be deterministic
* tie-breaking must be deterministic
* selection must be deterministic
* decision traces must be persisted
* orchestration stages must remain auditable
* LLM outputs must not bypass orchestration policies
* curriculum topology must remain external to the Tutor Orchestrator
