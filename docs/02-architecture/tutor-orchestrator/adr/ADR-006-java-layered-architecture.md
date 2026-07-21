# ADR-006 — Java Layered Architecture

## Status

Accepted

## Context

The Tutor Orchestrator will be implemented as an independent Java service within the AIGORA platform.

The service is responsible for coordinating deterministic pedagogical orchestration flows, including candidate generation, policy evaluation, ranking, selection, decision creation, integration with Curriculum Graph, and application result assembly.

As the system evolves, the Java codebase must preserve clear architectural boundaries between:

* domain logic
* application orchestration
* ports
* infrastructure adapters
* runtime configuration
* shared technical utilities

Without explicit layering, the implementation could evolve into a tightly coupled service where:

* use cases call infrastructure directly
* domain policies depend on gRPC or protobuf classes
* adapters contain orchestration logic
* infrastructure configuration owns business behavior
* external dependencies leak into the application core
* deterministic behavior becomes difficult to test and enforce

The Tutor Orchestrator requires a Java architecture that supports deterministic execution, testability, maintainability, and long-term architectural governance.

---

## Decision

The Tutor Orchestrator Java service will follow a layered Ports and Adapters architecture.

The Java implementation must be organized around the following architectural layers:

```text
domain
application
ports
adapters
infrastructure
shared
```

The expected root package is:

```text
com.aigora.tutororchestrator
```

The expected internal package structure is:

```text
src/main/java/com/aigora/tutororchestrator

├── application
├── domain
├── ports
├── adapters
├── infrastructure
└── shared
```

The Java service itself should live as an independently deployable service, for example:

```text
services/tutor-orchestrator
```

---

## Layer Responsibilities

### Domain

The domain layer owns deterministic orchestration concepts and business rules.

It contains:

* domain models
* value objects
* policies
* ranking abstractions
* selection abstractions
* decision concepts

The domain layer must remain framework-independent.

It must not depend on:

* Spring
* gRPC
* protobuf
* HTTP
* Neo4j
* infrastructure adapters

---

### Application

The application layer owns use case coordination.

It contains:

* commands
* results
* use cases
* application services
* orchestration flow coordination

The application layer may depend on:

* domain
* ports

It must not depend on:

* infrastructure implementations
* gRPC stubs
* protobuf models
* database clients
* transport adapters

---

### Ports

The ports layer defines explicit boundaries between the Tutor Orchestrator and external dependencies.

It contains:

* input ports
* output ports
* application-level integration contracts

Ports must remain technology-agnostic.

They must not expose:

* protobuf classes
* gRPC-specific models
* database records
* HTTP request/response models

---

### Adapters

The adapters layer translates external communication mechanisms into internal application contracts.

It contains:

* web adapters
* gRPC adapters
* mapper components
* transport error mappers

Adapters may depend on:

* ports
* application contracts
* infrastructure libraries

Adapters must not own:

* orchestration decisions
* policy rules
* ranking rules
* selection rules

---

### Infrastructure

The infrastructure layer owns runtime wiring and technical configuration.

It contains:

* dependency injection configuration
* gRPC client configuration
* observability wiring
* runtime configuration
* infrastructure-specific factories

Infrastructure must not contain business behavior.

---

### Shared

The shared layer may contain stable low-level utilities and technical primitives.

It must not become a dumping ground for orchestration logic.

Shared code must remain minimal and stable.

---

## Dependency Direction

Dependencies must point inward toward the orchestration core.

```text
infrastructure
    ↓
adapters
    ↓
ports
    ↓
application
    ↓
domain
```

Application may depend on ports and domain.

Ports may depend on stable domain concepts when necessary.

Adapters implement ports.

Infrastructure wires adapters.

Domain must not depend on any outer layer.

---

## Consequences

### Positive

* preserves deterministic domain isolation
* prevents infrastructure leakage into use cases
* improves testability of policies, ranking, and selection
* enables architecture tests to enforce dependency rules
* keeps gRPC and protobuf isolated from the application core
* supports independent evolution of infrastructure adapters
* improves onboarding through predictable package ownership
* aligns the Java implementation with the documented Tutor Orchestrator architecture

### Negative

* introduces more packages and architectural ceremony
* requires discipline to avoid bypassing ports
* may require additional mapper classes between layers
* simple features may require touching multiple layers
* architecture tests will be needed to prevent erosion

---

## Alternatives Considered

### Flat Package Structure

A flat package structure was rejected because it does not provide enough protection against coupling and responsibility leakage.

Rejected example:

```text
com.aigora.tutororchestrator
├── services
├── clients
├── models
└── utils
```

This structure makes it harder to distinguish orchestration logic from infrastructure concerns.

---

### Framework-Centric Spring Structure

A Spring-oriented structure was rejected as the primary architecture.

Rejected example:

```text
controller
service
repository
client
config
```

Although familiar, this structure tends to organize code by framework roles rather than business boundaries.

It can encourage use cases, infrastructure clients, and domain rules to mix inside service classes.

---

### Direct gRPC Usage from Use Cases

Direct gRPC usage from use cases was rejected.

Rejected flow:

```text
Use Case
    ↓
gRPC Stub
    ↓
Curriculum Graph
```

This would couple application orchestration to transport details and make the use case harder to test.

Accepted flow:

```text
Use Case
    ↓
CurriculumGraphClient
    ↓
GrpcCurriculumGraphClient
    ↓
Curriculum Graph gRPC API
```

---

## Constraints

* domain must remain framework-independent
* application must not depend on infrastructure
* use cases must depend on ports, not adapters
* protobuf and gRPC types must not enter domain or application logic
* infrastructure must not own orchestration decisions
* architecture tests should enforce dependency boundaries
* Java package structure must align with the documented architecture

---

## Related Documents

* [Java Architecture](../07-java-architecture/index.md)
* [Package Structure](../07-java-architecture/package-structure.md)
* [Layer Responsibilities](../07-java-architecture/layer-responsibilities.md)
* [Dependency Rules](../07-java-architecture/dependency-rules.md)
* [Ports and Adapters](../07-java-architecture/ports-and-adapters.md)
* [Curriculum Graph Application Port](../06-integration/curriculum-graph-application-port.md)
* [gRPC Infrastructure Adapter Strategy](../06-integration/grpc-infrastructure-adapter-strategy.md)
