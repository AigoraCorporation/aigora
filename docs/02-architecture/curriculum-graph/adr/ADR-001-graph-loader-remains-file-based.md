# ADR-001 — Graph Loading Remains File-Based

## Status
Accepted

## Context

The system requires a deterministic and reproducible way to load Curriculum Graph data.

Introducing persistence or external dependencies into the loading process would:

- increase coupling
- reduce testability
- reduce reproducibility
- mix loading responsibilities with publication responsibilities

## Decision

Graph loading must remain strictly file-based.

`LoadGraphUseCase` and the graph loading pipeline must:

- read from file-based sources only
- parse and validate file payloads
- map payloads into domain objects
- assemble a `CurriculumGraph`
- validate graph and version rules

They must not:

- access Neo4j
- publish graph data
- depend on persistence adapters
- mutate student state

## Consequences

### Positive

- deterministic behavior
- easy testing
- clear separation between loading and publication
- stable input model for CI and local development

### Negative

- persistence requires a separate publication step
- loading cannot answer persisted-state questions

## Constraints

- graph loading must not access Neo4j
- graph loading must not contain persistence logic
- graph loading must not call external APIs
