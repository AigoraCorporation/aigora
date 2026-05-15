# ADR-005 — Model Graph Loading as an Explicit Pipeline

## Status
Accepted

## Context

Graph loading is a deterministic sequence of steps:

- parse file
- validate schema
- map payload
- assemble graph
- validate graph
- validate version

Keeping this sequence inside one large method makes the flow harder to test and extend.

## Decision

Graph loading is modeled as an explicit pipeline.

The pipeline uses:

- `GraphLoadingPipeline`
- `GraphLoadingContext`
- `GraphLoadingStep`
- step implementations for parsing, validation, mapping, assembly, and version validation

## Consequences

### Positive

- each step can be tested independently
- the loading flow is easier to read
- future steps can be added without rewriting the use case
- failure diagnosis becomes clearer

### Negative

- more classes and files
- pipeline construction must be managed explicitly

## Constraints

- the loading pipeline must remain deterministic
- the pipeline must not access Neo4j
- persistence belongs to publication, not loading
