# ADR-007 — Command/Result Application Contracts

## Status

Accepted

## Context

The Tutor Orchestrator coordinates deterministic orchestration workflows through application use cases.

These use cases receive orchestration requests, interact with application ports, execute deterministic policies, invoke ranking strategies, and ultimately produce orchestration decisions.

As the architecture evolves, a consistent interaction model is required between:

* presentation adapters
* application use cases
* orchestration workflows
* integration boundaries

Without a formal application contract model, use cases could evolve toward:

* framework-dependent method signatures
* transport-specific request models
* inconsistent orchestration inputs
* inconsistent orchestration outputs
* exception-driven control flow
* reduced auditability and traceability

The project requires a stable and explicit application interaction model that remains independent from transport technologies and infrastructure concerns.

---

## Decision

The Tutor Orchestrator adopts a Command/Result application contract pattern.

Every application use case must expose:

```text
Command
    ↓
Use Case
    ↓
Result
```

The command represents the application request.

The result represents the application response.

The application layer becomes the owner of orchestration contracts.

---

## Architectural Model

```text
Presentation Layer
        ↓
Command
        ↓
Use Case
        ↓
Result
        ↓
Presentation Layer
```

Commands and results form the public application contract.

---

## Motivation

The command/result model provides:

* explicit use case boundaries
* deterministic orchestration contracts
* transport independence
* testability
* auditability
* stable application APIs

The model prevents infrastructure-specific concerns from leaking into orchestration workflows.

---

## Command Responsibilities

Commands represent application requests.

They contain:

* orchestration input data
* identifiers
* execution context
* correlation metadata

Commands do not contain:

* business logic
* infrastructure dependencies
* transport-specific behavior

Example:

```text
SelectNextLearningNodeCommand

studentId
currentNodeId
graphVersion
correlationId
```

Commands should be immutable.

---

## Result Responsibilities

Results represent application outcomes.

They contain:

* orchestration outputs
* decision identifiers
* execution metadata
* application-level failures

Results do not contain:

* transport status codes
* HTTP concepts
* gRPC concepts
* infrastructure exceptions

Example:

```text
SelectNextLearningNodeResult

decisionId
selectedNodeId
decisionReason
graphVersion
```

Results should be immutable.

---

## Application Layer Ownership

The application layer owns:

```text
Commands

Results

Use Cases
```

The domain layer owns:

```text
Policies

Ranking

Selection

Decision Rules
```

The infrastructure layer owns:

```text
HTTP

gRPC

Serialization

Transport Mapping
```

This separation preserves architectural boundaries.

---

## Deterministic Orchestration Flow

The command/result pattern supports deterministic orchestration.

```text
Command
    ↓
Load Context
    ↓
Execute Policies
    ↓
Generate Candidates
    ↓
Rank Candidates
    ↓
Create Decision
    ↓
Result
```

The same command should produce the same result when evaluated against the same deterministic state.

---

## Failure Handling

Application failures are represented through application-level results.

Examples:

```text
GraphUnavailable

InvalidGraphResponse

NoCandidateAvailable

DependencyTimeout
```

Use cases should expose stable failures.

Infrastructure exceptions must not leak into commands or results.

---

## Interaction with Application Ports

Use cases interact with external systems through ports.

```text
Command
    ↓
Use Case
    ↓
Application Port
    ↓
Infrastructure Adapter
    ↓
External Service
```

Commands and results remain independent from infrastructure implementations.

---

## Consequences

### Positive

* explicit application contracts
* improved testability
* deterministic orchestration boundaries
* transport independence
* easier contract evolution
* clearer auditability
* consistent use case design
* reduced infrastructure leakage

### Negative

* additional contract classes
* more mapping responsibilities
* increased architectural ceremony
* larger number of application objects

These tradeoffs are considered acceptable.

---

## Alternatives Considered

### Direct Method Parameters

Rejected example:

```java
selectNextLearningNode(
    String studentId,
    String nodeId,
    String graphVersion
)
```

Rejected because:

* weak contract evolution
* inconsistent signatures
* reduced auditability
* poor extensibility

---

### Transport-Centric Models

Rejected example:

```text
HttpRequest
GrpcRequest
ProtoRequest
```

Rejected because:

* couples application logic to transport technologies
* violates dependency inversion
* reduces portability

---

### Exception-Driven Application Flow

Rejected example:

```text
Use Case
    ↓
Exception
    ↓
Presentation Layer
```

Rejected because:

* failures become inconsistent
* orchestration outcomes become harder to reason about
* deterministic behavior becomes less explicit

The project prefers stable application-level result contracts.

---

## Constraints

* every use case must expose a command
* every use case must expose a result
* commands must be immutable
* results must be immutable
* commands must not contain business logic
* results must not expose transport concerns
* infrastructure exceptions must not leak outside adapters
* use cases must remain transport-independent

---

## Examples

Initial use cases are expected to follow this model:

```text
SelectNextLearningNode
    Command
    Result

SelectRegressionNode
    Command
    Result

EvaluateLearningProgress
    Command
    Result
```

Future use cases should follow the same pattern.

---

## Relationship to Other Decisions

This ADR builds upon:

* ADR-001 Deterministic-First Orchestration
* ADR-002 Curriculum Graph Integration via gRPC
* ADR-006 Java Layered Architecture

The command/result model provides the application contract foundation required by those architectural decisions.

---

## Related Documents

* [Application Contracts](../07-java-architecture/application-contracts.md)
* [Use Cases](../03-orchestration/use-cases.md)
* [Java Architecture](../07-java-architecture/index.md)
* [Deterministic Orchestration](../03-orchestration/deterministic-orchestration.md)
* [Application Error Model](../07-java-architecture/application-error-model.md)
