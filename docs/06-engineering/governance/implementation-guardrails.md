# Implementation Guardrails

## Purpose

Enforce architectural consistency and prevent design violations.

---

## Architecture

### domain

* entities
* value objects
* pure business rules

### application

* services
* loaders
* exporters
* ports

### infrastructure

* database (Neo4j)
* filesystem
* adapters

---

## Rules

* GraphLoader is strictly file-based
* Neo4j access is restricted to GraphRepository
* GraphPublicationService owns orchestration
* CSV is a derived artifact only
* Existing validations must be reused

---

## Responsibility Boundaries

| Layer          | Scope                 |
| -------------- | --------------------- |
| domain         | business rules only   |
| application    | orchestration only    |
| infrastructure | external integrations |

---

## Prohibited

* GraphLoader accessing persistence
* Cypher outside repositories
* Domain depending on infrastructure
* Generic utility classes
* Validation duplication
* Business logic in CLI
* Non-centralized queries

---

## Code Constraints

* Single responsibility per class
* Explicit, intention-revealing names
* No generic helpers
* No hidden logic

---

## Compliance

All implementations must:

* Follow the assigned layer
* Respect the defined structure
* Adhere to documented architecture
* Comply with these guardrails

---

## Pre-Commit Checks

* [x] Correct layer placement
* [x] No domain logic in infrastructure
* [x] No persistence outside repositories
* [x] No duplicated validation
* [x] Structure is respected

---

## Enforcement

Non-compliant implementations must be rejected in code review.

