# Engineering Policies

This document defines the engineering policies that govern how
AIGORA's software is designed, implemented, and evolved.

These policies are not aspirational guidelines.  
They are **operative constraints** enforced as part of the development process.

The goal is to ensure:

- Intentional design over accidental complexity
- Correctness by construction
- Long-term maintainability
- Alignment between code, domain, and behavior

------------------------------------------------------------------------

# Overview

AIGORA's engineering practices are grounded in three complementary
methodology families and a set of invariant design principles:

| Category                    | Practices                          |
|----------------------------|------------------------------------|
| **Process methodologies**  | BDD, DDD                           |
| **Design principles**      | SOLID, DRY, KISS, YAGNI            |
| **Data invariants**        | ACID                               |
| **Architectural constraints** | Clean Architecture, Separation of Concerns |

Each section below defines the practice, its operative rule inside AIGORA,
and the violation signals that must trigger a review or refactor.

------------------------------------------------------------------------

# 1. BDD — Behavior-Driven Development

## Definition

Express requirements as concrete examples of system behavior, written in
a shared language understood by both technical and non-technical stakeholders.

## Operative rules

- Acceptance criteria in GitHub Issues must be expressed as
  **Given / When / Then** scenarios.
- Integration and end-to-end tests must map to acceptance scenarios.
- Tests must use the language of the domain, not implementation details.

## Example

```

Given a student with no prior interaction on topic "linear equations"
When the tutor selects the next exercise
Then the recommended difficulty level is "introductory"

```

## Violation signals

- Acceptance criteria described only as implementation steps
- Tests validating internal details instead of observable behavior
- Mixing domain language with technical terms in tests

------------------------------------------------------------------------

# 2. DDD — Domain-Driven Design

## Definition

Structure the codebase around the business domain. The code must reflect the
**Ubiquitous Language** used across domain, documentation, and implementation.

## Tactical patterns in use

| Pattern            | Application in AIGORA                               |
|--------------------|-----------------------------------------------------|
| **Entity**         | Curriculum nodes, student records                   |
| **Value Object**   | Topic identifiers, skill levels                     |
| **Aggregate**      | Curriculum graph, student model                     |
| **Repository**     | Persistence interface for aggregates                |
| **Domain Service** | Recommendation logic, assessment logic              |
| **Domain Event**   | Skill mastered, session started                     |

## Layered architecture

```

domain/          ← Pure business logic
application/     ← Use cases and orchestration
infrastructure/  ← External systems and adapters

```

Dependencies must point **inward only**.

## Operative rules

- Domain must not depend on infrastructure
- Naming must align with domain definitions
- Business rules must not exist outside domain/application layers

## Violation signals

- Domain importing frameworks or database libraries
- Business logic inside controllers or repositories
- Technical terms leaking into domain models

------------------------------------------------------------------------

# 3. SOLID Principles

## SRP — Single Responsibility

Each component must have one reason to change.

## OCP — Open/Closed

Extend behavior without modifying stable code.

## LSP — Substitution

Subtypes must preserve behavior contracts.

## ISP — Interface Segregation

Prefer small, focused interfaces.

## DIP — Dependency Inversion

Depend on abstractions, not implementations.

------------------------------------------------------------------------

# 4. DRY — Don't Repeat Yourself

## Definition

Each piece of knowledge must have a single authoritative representation.

## Operative rules

- Duplication of logic is a defect
- Shared rules must be centralized
- Configuration must not be duplicated

## Violation signals

- Repeated validation logic
- Magic values in multiple places
- Copy-pasted code blocks

------------------------------------------------------------------------

# 5. KISS — Keep It Simple

## Definition

Prefer the simplest solution that correctly solves the problem.

## Operative rules

- Avoid unnecessary abstractions
- Favor readability over cleverness
- Keep functions and modules small

## Violation signals

- Over-engineered designs
- Deep abstraction layers without need
- Hard-to-read logic

------------------------------------------------------------------------

# 6. YAGNI — You Aren't Gonna Need It

## Definition

Do not implement features before they are required.

## Operative rules

- No implementation without a related issue
- Avoid speculative abstractions
- Remove unused code

## Violation signals

- Dead code
- Unused configuration
- Features without use cases

------------------------------------------------------------------------

# 7. ACID — Data Invariants

## Definition

All state mutations must respect:

- Atomicity
- Consistency
- Isolation
- Durability

## Operative rules

- Use transactions for writes
- Ensure idempotent operations
- Never leave partial state

## Violation signals

- Partial writes
- Silent failures
- Non-idempotent operations

------------------------------------------------------------------------

# 8. Separation of Concerns

## Definition

Different responsibilities must be isolated.

## Operative rules

- Separate input, logic, and output
- Keep domain independent of serialization
- Avoid mixing layers

------------------------------------------------------------------------

# 9. Fail Fast

## Definition

Detect and signal errors as early as possible.

## Operative rules

- Validate at boundaries
- Raise explicit errors
- Never allow invalid state

## Violation signals

- Silent failures
- Late validation
- Invalid objects in memory

------------------------------------------------------------------------

# Enforcement

These policies are enforced through:

| Mechanism              | Scope                              |
|-----------------------|------------------------------------|
| PR review             | Design and behavior validation     |
| CI checks             | Code quality and structure         |
| Integration tests     | Behavior validation                |
| Architecture docs     | Domain consistency                 |

Reviewers must flag violations before approval.

------------------------------------------------------------------------

# References

- docs/02-architecture/overview.md
- docs/06-engineering/workflow/development-workflow.md
- docs/06-engineering/workflow/pull-request-policy.md
- docs/06-engineering/conventions/commits.md


