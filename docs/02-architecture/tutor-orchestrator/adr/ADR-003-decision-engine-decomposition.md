# ADR-003 — Decision Engine Decomposition

## Status

Accepted

## Context

The Tutor Orchestrator is responsible for producing deterministic pedagogical decisions.

A single component responsible for orchestration coordination, policy evaluation, ranking, selection, and auditability would:

* accumulate multiple responsibilities
* become difficult to maintain
* increase coupling between decision concerns
* reduce testability
* complicate future evolution
* make ownership boundaries unclear

As orchestration capabilities evolve, different decision concerns require independent evolution while preserving deterministic behavior.

The architecture requires a clear separation between decision coordination, policy evaluation, candidate preference, final selection, and decision traceability.

## Decision

The Decision Engine must be decomposed into specialized engines.

Each engine must own a single orchestration responsibility.

The Decision Engine architecture must be composed of:

* Orchestration Engine
* Policy Engine
* Strategy Engine
* Selection Engine
* Auditability Engine

The engines are responsible for:

| Engine               | Responsibility                                     |
| -------------------- | -------------------------------------------------- |
| Orchestration Engine | Coordinate orchestration execution flow            |
| Policy Engine        | Determine candidate eligibility                    |
| Strategy Engine      | Determine candidate preference                     |
| Selection Engine     | Produce final orchestration commitment             |
| Auditability Engine  | Preserve decision traceability and reproducibility |

The Decision Engine acts as the coordination layer between these specialized engines.

The architecture must not:

* centralize all decision logic in a single component
* mix policy evaluation with ranking logic
* mix ranking logic with selection logic
* mix decision-making with auditability concerns
* bypass explicit ownership boundaries

## Consequences

### Positive

* clear responsibility boundaries
* improved maintainability
* easier testing
* improved auditability
* simpler reasoning about orchestration behavior
* independent evolution of orchestration concerns
* better alignment with bounded context principles
* reduced architectural complexity over time

### Negative

* additional architectural components
* increased documentation requirements
* additional coordination between engines
* slightly more complex runtime flow

## Constraints

* each engine must own a single orchestration concern
* policy evaluation must remain independent from ranking
* ranking must remain independent from selection
* auditability must remain independent from decision-making
* orchestration flow must remain deterministic
* decision ownership boundaries must remain explicit
* engine responsibilities must not overlap
