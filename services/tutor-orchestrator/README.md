
# AIGORA Tutor Orchestrator

The Tutor Orchestrator is the deterministic decision engine responsible for selecting the next pedagogical action for a student.

It coordinates curriculum traversal, student state evaluation, policy execution, candidate ranking, and deterministic decision making while remaining independent from transport protocols and infrastructure implementations.

---

## Responsibilities

The Tutor Orchestrator is responsible for:

- Selecting the next learning node
- Selecting regression nodes
- Evaluating learning progress
- Executing deterministic pedagogical policies
- Ranking learning candidates
- Producing auditable orchestration decisions

The orchestrator does **not** perform:

- LLM inference
- Curriculum storage
- Student persistence
- Graph database access
- UI rendering

Those responsibilities belong to other AIGORA components.

---

## Architecture

The module follows a Clean Architecture style.

```
Presentation
    ↓
Application
    ↓
Domain
    ↓
Infrastructure
```

Core design principles:

- Deterministic First
- Framework Independent
- Domain Driven Design
- Dependency Inversion
- Immutable Domain Models
- Explicit Use Cases
- Auditable Decisions

---

## Module Structure

```
src
 ├── application
 ├── domain
 ├── infrastructure
 ├── presentation
 └── shared
```

---

## Main Use Cases

- SelectNextLearningNode
- SelectRegressionNode
- EvaluateLearningProgress

---

## Decision Pipeline

```
Evaluate Learning Progress
            │
            ▼
Regression Required?
      │          │
     Yes         No
      │           │
      ▼           ▼
Regression   Learning Completed?
Selection          │
                   │
              Yes      No
               │        │
               ▼        ▼
         Next Node   Continue
         Selection   Learning
```

---

## Testing

The project includes:

- Unit Tests
- Integration Tests
- Contract Tests
- Test Builders
- Test Fixtures
- Fake Implementations

---

## Build

```bash
mvn clean test
```

---

## Status

Current version:

**v0.3.0**

Status:

**Core Runtime Complete**

The deterministic orchestration engine is considered stable for the current project phase.# AIGORA Tutor Orchestrator



The Tutor Orchestrator is the deterministic decision engine responsible for selecting the next pedagogical action for a student.



It coordinates curriculum traversal, student state evaluation, policy execution, candidate ranking, and deterministic decision making while remaining independent from transport protocols and infrastructure implementations.



---



## Responsibilities



The Tutor Orchestrator is responsible for:



- Selecting the next learning node

- Selecting regression nodes

- Evaluating learning progress

- Executing deterministic pedagogical policies

- Ranking learning candidates

- Producing auditable orchestration decisions



The orchestrator does **not** perform:



- LLM inference

- Curriculum storage

- Student persistence

- Graph database access

- UI rendering



Those responsibilities belong to other AIGORA components.



---



## Architecture



The module follows a Clean Architecture style.



```

Presentation

    ↓

Application

    ↓

Domain

    ↓

Infrastructure

```



Core design principles:



- Deterministic First

- Framework Independent

- Domain Driven Design

- Dependency Inversion

- Immutable Domain Models

- Explicit Use Cases

- Auditable Decisions



---



## Module Structure



```

src

 ├── application

 ├── domain

 ├── infrastructure

 ├── presentation

 └── shared

```



---



## Main Use Cases



- SelectNextLearningNode

- SelectRegressionNode

- EvaluateLearningProgress



---



## Decision Pipeline



```

Evaluate Learning Progress

    │

    ▼

Regression Required?

    │          │

    Yes         No

    │           │

    ▼           ▼

Regression   Learning Completed?

Selection          │

    │

    Yes      No

    │        │

    ▼        ▼

    Next Node   Continue

    Selection   Learning

```



---



## Testing



The project includes:



- Unit Tests

- Integration Tests

- Contract Tests

- Test Builders

- Test Fixtures

- Fake Implementations



---



## Build



```bash

mvn clean test

```



---



## Status



Current version:



**v0.3.0**



Status:



**Core Runtime Complete**



The deterministic orchestration engine is considered stable for the current project phase.
