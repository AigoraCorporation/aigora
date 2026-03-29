# SWE Agent Policies

This document defines the engineering methodology policies that govern how
AIGORA's software agents — and contributors acting as agents — must design,
implement, and evolve code.

These policies are not aspirational guidelines.  
They are **operative constraints** enforced as part of the development process.

The goal is to ensure:

-   Intentional design over accidental complexity
-   Correctness by construction, not by luck
-   Long-term maintainability
-   Alignment between code, domain, and tests

------------------------------------------------------------------------

# Overview

AIGORA's engineering practices are grounded in three complementary
methodology families and a set of invariant design mantras:

| Category              | Practices                          |
|-----------------------|------------------------------------|
| **Process methodologies** | TDD, BDD, DDD                  |
| **Design principles** | SOLID, DRY, KISS, YAGNI            |
| **Data invariants**   | ACID                               |
| **Architectural constraints** | Clean Architecture, Separation of Concerns |

Each section below defines the practice, its operative rule inside AIGORA,
and the violation signals that must trigger a review or refactor.

------------------------------------------------------------------------

# 1. TDD — Test-Driven Development

## Definition

Write the failing test first, then write the minimum code to pass it,
then refactor. No production code exists without a corresponding test.

## Red → Green → Refactor cycle

1.  **Red** — Write a failing unit test that specifies the desired behavior.
2.  **Green** — Write the simplest code that makes the test pass.
3.  **Refactor** — Improve the internal structure without changing behavior.
    All tests must remain green after refactoring.

## Operative rules

-   No PR may introduce production logic without accompanying tests.
-   New domain logic that lacks tests is considered incomplete and cannot
    be merged.
-   Minimum coverage threshold is defined per module in the CI configuration.
-   Tests must be deterministic. Flaky tests must be quarantined immediately
    and treated as bugs.

## Violation signals

-   Coverage drops after a feature PR.
-   Production module exists with no corresponding test file.
-   Tests are written after the implementation as an afterthought.

------------------------------------------------------------------------

# 2. BDD — Behavior-Driven Development

## Definition

Express requirements as concrete examples of system behavior, written in
a shared language understood by both technical and non-technical stakeholders.

## Operative rules

-   Acceptance criteria in GitHub Issues must be expressed as
    **Given / When / Then** scenarios.
-   Integration and end-to-end tests must map 1:1 to acceptance scenarios.
-   Tests must use the language of the domain, not the language of the
    implementation.

## Example

```
Given a student with no prior interaction on topic "linear equations"
When the tutor selects the next exercise
Then the recommended difficulty level is "introductory"
```

## Violation signals

-   Acceptance criteria in Issues expressed only as implementation tasks
    ("add method X to class Y") with no observable behavior described.
-   Integration tests that test implementation details rather than outcomes.
-   Domain terms and implementation terms mixed in test naming.

------------------------------------------------------------------------

# 3. DDD — Domain-Driven Design

## Definition

Structure the codebase around the business domain. The code must speak the
**Ubiquitous Language** of the domain — terms used by domain experts must
appear identically in code, documentation, and conversations.

## Tactical patterns in use

| Pattern            | Application in AIGORA                               |
|--------------------|-----------------------------------------------------|
| **Entity**         | Nodes in the curriculum graph, student records      |
| **Value Object**   | Topic identifiers, skill codes, competency levels   |
| **Aggregate**      | Curriculum graph, student model                     |
| **Repository**     | Persistence interface for aggregates                |
| **Domain Service** | Assessment engine logic, recommendation logic       |
| **Domain Event**   | Skill mastered, session started, hint requested     |

## Layered architecture

Code must be organized into these layers:

```
domain/          ← Pure business logic. No I/O, no framework dependencies.
application/     ← Use cases and orchestration. Depends only on domain.
infrastructure/  ← Databases, external APIs, adapters. Implements domain interfaces.
```

Dependencies point **inward only**. Infrastructure depends on domain, never
the reverse.

## Operative rules

-   A domain class must never import from `infrastructure`.
-   Every new concept introduced in code must first be validated against the
    domain glossary (see `docs/02-architecture/`).
-   Naming inconsistencies between domain documents and code are treated as
    defects.

## Violation signals

-   Domain models importing from ORM or HTTP libraries.
-   Business rules implemented inside HTTP handlers or database repositories.
-   Technical terms (e.g. `db_row`, `api_response`) leaking into domain classes.
-   A concept exists in code that has no corresponding definition in the
    architecture docs.

------------------------------------------------------------------------

# 4. SOLID Principles

## Single Responsibility Principle (SRP)

A module, class, or function must have **one reason to change**.

-   Each class owns one cohesive concept.
-   A function does one thing and names that thing.
-   Violation: a class that builds queries, formats output, *and* sends
    notifications.

## Open/Closed Principle (OCP)

Software entities must be **open for extension, closed for modification**.

-   New behavior is added by extending, not by editing existing stable code.
-   Use composition, protocols/interfaces, and strategy patterns.
-   Violation: adding an `if` branch to handle a new type in an existing
    function that was already stable.

## Liskov Substitution Principle (LSP)

Subtypes must be **substitutable** for their base types without altering
program correctness.

-   A subclass must fulfill the full contract of its parent.
-   Violation: overriding a method in a subclass in a way that raises
    exceptions the parent never raised, or silently drops behavior.

## Interface Segregation Principle (ISP)

Clients must not be forced to depend on interfaces they do not use.

-   Prefer small, focused protocols over large, general ones.
-   Violation: a repository interface that forces every caller to implement
    ten methods when only two are needed.

## Dependency Inversion Principle (DIP)

High-level modules must not depend on low-level modules.  
Both must depend on **abstractions**.

-   Domain and application layers depend on interfaces, not concrete
    implementations.
-   Concrete implementations (e.g. `PostgresRepository`) are injected at
    the infrastructure boundary.
-   Violation: use case class directly instantiating `SQLAlchemySession`.

------------------------------------------------------------------------

# 5. DRY — Don't Repeat Yourself

## Definition

Every piece of knowledge must have a **single, authoritative representation**
in the system.

## Operative rules

-   Duplication of logic is a defect, not a style issue.
-   Before writing new logic, search for an existing implementation.
-   Duplication of *structure* (e.g. two similar data classes) is acceptable
    only if the two things represent genuinely different domain concepts.
-   Configuration values must not be inlined — they live in dedicated
    configuration modules or environment variables.

## Important distinction

DRY applies to **knowledge** (logic, rules, configuration), not to code
characters. Two blocks of code that look similar but represent different
concepts should **not** be merged. Premature DRY creates wrong abstractions.

## Violation signals

-   Same validation rule implemented in multiple modules.
-   Magic numbers or strings inlined in multiple locations.
-   Copy-pasted logic blocks with minor variations.

------------------------------------------------------------------------

# 6. KISS — Keep It Simple, Stupid

## Definition

Prefer the simplest solution that correctly solves the problem.
Complexity must be justified by a real requirement, not by anticipation.

## Operative rules

-   Do not build abstractions for hypothetical future needs (see YAGNI).
-   Favor readable, linear code over clever, compact code.
-   If a reviewer needs more than a few seconds to understand a block,
    it requires simplification or documentation.
-   Cyclomatic complexity per function must be kept low (max 10 is a
    reasonable baseline).

## Violation signals

-   Over-engineered class hierarchies for a problem that a function solved.
-   Indirection layers added "for flexibility" with no current use case.
-   Complex one-liners that save lines but lose clarity.

------------------------------------------------------------------------

# 7. YAGNI — You Aren't Gonna Need It

## Definition

Do not implement functionality until it is actually required.

## Operative rules

-   Features not tied to an open Issue must not be implemented.
-   Generic frameworks, plugin systems, and extension points must not be
    built unless an immediate use case exists.
-   Code that is "commented out" or "disabled for now" must be deleted,
    not left in the codebase.

## Violation signals

-   PR includes logic with no corresponding acceptance criterion.
-   Methods exist that are never called by any current execution path.
-   Configuration options that control non-existent features.

------------------------------------------------------------------------

# 8. ACID — Data Operation Invariants

## Definition

All operations that mutate persistent state must respect ACID properties:

| Property        | Meaning                                                     |
|-----------------|-------------------------------------------------------------|
| **Atomicity**   | An operation either completes fully or has no effect.       |
| **Consistency** | State transitions must leave data in a valid state.         |
| **Isolation**   | Concurrent operations must not produce inconsistent reads.  |
| **Durability**  | Committed data survives system failures.                    |

## Operative rules

-   All write operations in repositories must be wrapped in explicit
    transactions.
-   Partial writes that leave the system in an inconsistent state are
    treated as critical bugs.
-   Repository methods must not silently swallow exceptions that signal
    constraint violations.
-   Bulk operations (e.g. graph ingestion) must be idempotent and
    transactional.

## Violation signals

-   A repository method performs multiple writes without a transaction.
-   Error handling in persistence code uses bare `except: pass`.
-   Graph update routines that are not idempotent (running twice produces
    different state).

------------------------------------------------------------------------

# 9. Separation of Concerns (SoC)

## Definition

Different responsibilities must be handled by different modules.
No module may carry concerns that belong to a different layer.

## Operative rules

-   Input parsing, business logic, and output formatting are always in
    separate locations.
-   A function that queries data must not also format the response for
    the HTTP layer.
-   Domain rules must not reference serialization formats (JSON, YAML,
    Protobuf).

------------------------------------------------------------------------

# 10. Fail Fast

## Definition

Errors must be detected and signaled **as early as possible** in the
execution path.

## Operative rules

-   Validate inputs at system boundaries (API handlers, file loaders,
    CLI entry points). Trust validated data inside the domain.
-   Raise exceptions with clear, actionable messages. Never return `None`
    to signal a failure silently.
-   Constructors and factory methods must reject invalid state immediately.
    An invalid object must never be constructed.

## Violation signals

-   Validation deferred to the persistence layer when it could be done
    at the application boundary.
-   Functions returning `None` or empty collections as an error signal
    without any log or exception.

------------------------------------------------------------------------

# Enforcement

These policies are enforced through multiple mechanisms:

| Mechanism                  | Scope                                      |
|----------------------------|--------------------------------------------|
| CI lint checks             | Code style, import layering                |
| Coverage gates             | TDD compliance                             |
| PR template review         | BDD acceptance criteria presence           |
| Architecture ADRs          | DDD naming and layering decisions          |
| Code review checklist      | SOLID, DRY, KISS, YAGNI violations         |
| Integration test suite     | ACID transaction correctness               |

Reviewers are expected to flag violations of any policy defined here
before approving a Pull Request.

------------------------------------------------------------------------

# References

-   `docs/02-architecture/overview.md` — system layering
-   `docs/06-operations/workflow.md` — development lifecycle
-   `docs/06-operations/pull-request-policy.md` — PR requirements
-   `docs/conventions/commits.md` — commit message standards
