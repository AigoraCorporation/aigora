# ADR-005 — Auditability-First Architecture

## Status

Accepted

## Context

The Tutor Orchestrator is responsible for making pedagogical decisions that directly influence student progression.

As orchestration capabilities evolve, decisions become increasingly difficult to understand, validate, and reproduce without explicit traceability mechanisms.

A decision architecture without auditability would:

- make decision reconstruction difficult
- reduce pedagogical transparency
- complicate debugging
- reduce trust in orchestration outcomes
- make governance harder to enforce
- increase operational complexity
- make future adaptive orchestration harder to validate

The architecture requires a first-class mechanism to explain, reconstruct, and reproduce orchestration decisions.

## Decision

The Tutor Orchestrator must adopt an auditability-first architecture.

Auditability must be treated as a core architectural responsibility rather than an operational concern.

Every orchestration decision must produce sufficient evidence to support:

- decision reconstruction
- policy traceability
- ranking traceability
- selection traceability
- graph version traceability
- orchestration observability
- reproducibility

The architecture must include a dedicated Auditability Engine responsible for:

- collecting decision evidence
- generating decision traces
- preserving orchestration history
- supporting governance requirements
- enabling decision reconstruction

The architecture must persist references to:

- graph version
- candidate set
- policy execution results
- ranking results
- selection results
- orchestration metadata

The architecture must not:

- allow opaque decision-making
- hide policy outcomes
- discard ranking evidence
- discard selection evidence
- allow decisions that cannot be reconstructed
- bypass auditability requirements

## Consequences

### Positive

- improved decision transparency
- easier debugging
- reproducible orchestration outcomes
- stronger governance model
- improved platform accountability
- support for decision reconstruction
- improved recommendation explainability
- foundation for future adaptive orchestration

### Negative

- additional implementation complexity
- increased storage requirements
- larger orchestration payloads
- additional trace management responsibilities

## Constraints

- every orchestration decision must be traceable
- policy execution must generate audit evidence
- ranking execution must generate audit evidence
- selection execution must generate audit evidence
- graph version references must be persisted
- decision traces must support reconstruction
- auditability concerns must remain independent from decision-making
- orchestration stages must remain observable
- deterministic reproducibility must be preserved