# ADR-004 — Use Command/Result Contracts for Use Cases

## Status
Accepted

## Context

Use cases can become difficult to evolve when they expose many positional parameters or return unstructured dictionaries.

The Curriculum Graph application needs stable use case contracts that can be consumed by APIs, CLIs, tests, and future workers.

## Decision

Each application use case should receive a command object and return a result object.

Example:

```text
LoadGraphCommand → LoadGraphUseCase.execute(command) → LoadGraphResult
```

## Consequences

### Positive

- explicit application input/output contracts
- easier testing
- easier API mapping
- less fragile method signatures
- better separation between HTTP schemas and application contracts

### Negative

- additional small classes per use case
- more files to maintain

## Constraints

- commands must represent application input, not HTTP request schemas
- results must represent application output, not HTTP response schemas
- use cases should expose `execute(command)` as the primary operation
