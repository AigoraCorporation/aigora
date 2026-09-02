# ADR-008 — Learning Session Ownership and Bounded-Context Boundaries

- **Status:** Accepted
- **Date:** 2026-07-28
- **Decision Owners:** AIGORA Architecture
- **Milestone:** v0.3.1 — Learning Session Orchestration
- **Related ADRs:** ADR-001, ADR-003, ADR-006, ADR-007
- **Related Issues:** #259, #261, #262, #263, #264, #265, #266, #267, #283, #284, #285, #286, #287

---

## 1. Context

AIGORA requires a clear architectural boundary for the complete Learning Session lifecycle.

Session-related responsibilities currently interact with multiple components:

- Learning Session Engine;
- Tutor Orchestrator;
- Assessment Engine;
- Student Model;
- Curriculum Graph;
- Retrieval Layer;
- LLM Gateway.

Without a formal ownership decision, the implementation could introduce:

- duplicated Learning Session state;
- more than one component mutating the same session;
- shared persistence across bounded contexts;
- assessment concerns leaking into orchestration;
- orchestration concerns leaking into session execution;
- bidirectional dependencies;
- unclear recovery authority;
- inconsistent event ownership;
- multiple sources of truth;
- a second orchestration engine with overlapping responsibility.

The existing architecture already establishes important principles:

1. the Tutor Orchestrator owns pedagogical decision-making;
2. execution and user-facing learning flow remain separate from decision-making;
3. bounded contexts must integrate through explicit contracts;
4. each aggregate must have exactly one authoritative owner;
5. no component may access another component's persistence directly.

This ADR defines:

- the authoritative owner of Learning Session state;
- the bounded-context boundary;
- state mutation authority;
- command and event ownership;
- cross-component responsibilities;
- owned, referenced, cached, derived, and transient data;
- synchronous and asynchronous interaction directions;
- prohibited dependencies.

Detailed lifecycle states and transitions are deferred to ADR-009.

Event publication and consistency guarantees are deferred to ADR-010.

Persistence and recovery strategy are deferred to ADR-011.

---

## 2. Decision

### 2.1 Authoritative owner

The **Learning Session Engine is the authoritative owner of the `LearningSession` aggregate and the Learning Session bounded context**.

The Learning Session Engine owns:

- Learning Session identity;
- session lifecycle state;
- current learning node reference;
- current exercise reference;
- exercise-attempt state;
- session version;
- legal session transitions;
- session invariants;
- session commands;
- session domain events;
- session persistence abstraction;
- session recovery metadata;
- authority to commit mutations to the `LearningSession` aggregate.

No other AIGORA component may directly mutate Learning Session state.

### 2.2 Tutor Orchestrator responsibility

The **Tutor Orchestrator owns pedagogical decision-making**, not the Learning Session aggregate.

It owns:

- candidate generation;
- eligibility filtering;
- regression policies;
- completion policies related to pedagogical selection;
- deterministic ranking;
- deterministic node selection;
- `OrchestrationDecision`;
- decision reasons;
- pedagogical decision trace;
- orchestration policy execution;
- graph-version-aware decision semantics.

The Tutor Orchestrator receives an immutable orchestration request and returns an immutable orchestration result.

The Tutor Orchestrator does not:

- load or persist the `LearningSession` aggregate;
- mutate session lifecycle state;
- own exercise-attempt state;
- render or deliver exercises;
- become the system of record for Student Model state;
- become the system of record for Assessment Engine data;
- become the system of record for Curriculum Graph data.

### 2.3 Separation between decision and execution

The architecture preserves the distinction between:

```text
Tutor Orchestrator
    decides what should happen next

Learning Session Engine
    validates and executes the session transition
```

A pedagogical decision returned by the Tutor Orchestrator does not mutate session state by itself.

The Learning Session Engine must:

1. receive the decision;
2. validate session identity;
3. validate expected session version;
4. validate causality;
5. validate that the decision is legal for the current session state;
6. apply the decision through the aggregate;
7. persist the new session version;
8. publish the resulting committed events.

### 2.4 Mutation authority

Only the Learning Session Engine may execute commands that mutate the `LearningSession` aggregate.

Allowed mutation path:

```text
External interaction or internal session trigger
    ↓
Learning Session application use case
    ↓
LearningSession aggregate
    ↓
LearningSessionRepository
    ↓
Committed session events
```

Pedagogical decision path:

```text
Learning Session Engine
    ↓ immutable orchestration request
Tutor Orchestrator
    ↓ immutable OrchestrationDecision
Learning Session Engine
    ↓ validates and applies decision
LearningSession aggregate
```

---

## 3. Bounded Contexts

The following bounded contexts remain independent.

| Bounded context | Authoritative ownership |
|---|---|
| Learning Session Engine | Learning Session lifecycle, attempt state, session version, session commands and session events |
| Tutor Orchestrator | Pedagogical decision process, candidate ranking, policy execution, node selection and decision evidence |
| Assessment Engine | Assessment result, scoring semantics, confidence and assessment evidence |
| Student Model | Learner knowledge, mastery, misconceptions, confidence and learner-state version |
| Curriculum Graph | Curriculum topology, node metadata, prerequisites, traversal semantics and graph version |
| Retrieval Layer | Retrieved knowledge, source evidence and retrieval metadata |
| LLM Gateway | Model-provider abstraction, invocation policy, provider routing and generation execution |

No bounded context may use another bounded context's database as an integration mechanism.

---

## 4. Component Responsibilities

### 4.1 Learning Session Engine

#### Responsible for

- creating Learning Sessions;
- maintaining session identity;
- maintaining lifecycle state;
- maintaining session version;
- associating the current node;
- associating the current exercise;
- recording exercise attempts;
- recording exercise completion;
- validating legal session transitions;
- coordinating assessment requests;
- requesting pedagogical decisions;
- validating and applying orchestration decisions;
- persisting Learning Session state;
- emitting session events;
- enforcing session idempotency;
- enforcing concurrency rules;
- coordinating session recovery.

#### Not responsible for

- computing assessment scores;
- owning learner mastery;
- traversing Curriculum Graph persistence directly;
- generating pedagogical candidates;
- ranking pedagogical candidates;
- selecting the next node;
- invoking LLM providers directly;
- owning retrieved educational content.

### 4.2 Tutor Orchestrator

#### Responsible for

- deterministic pedagogical decisions;
- candidate generation;
- candidate eligibility evaluation;
- policy execution;
- deterministic ranking;
- candidate selection;
- completion decisions;
- regression decisions;
- explicit decision reasons;
- decision traceability;
- graph-version-aware evidence;
- reconstructable decision traces.

#### Not responsible for

- owning Learning Session state;
- persisting Learning Session state;
- controlling session lifecycle;
- rendering exercises;
- receiving raw user interaction as authoritative state;
- directly mutating Student Model state;
- directly mutating Curriculum Graph state;
- implementing Assessment Engine scoring;
- bypassing the LLM Gateway.

### 4.3 Assessment Engine

#### Responsible for

- evaluating completed attempts;
- computing assessment results;
- exposing assessment confidence;
- exposing assessment evidence;
- versioning assessment contracts;
- preserving assessment-specific semantics.

#### Not responsible for

- mutating Learning Session state;
- selecting the next node;
- owning learner mastery;
- updating Curriculum Graph state;
- applying session transitions.

### 4.4 Student Model

#### Responsible for

- learner knowledge state;
- mastery estimates;
- confidence values;
- misconceptions;
- learner-state history;
- learner-state versioning.

#### Not responsible for

- owning session lifecycle;
- storing Learning Session as canonical operational state;
- selecting the next node;
- mutating Curriculum Graph state;
- controlling exercise delivery.

### 4.5 Curriculum Graph

#### Responsible for

- curriculum topology;
- node identity;
- node metadata;
- prerequisite relationships;
- graph traversal semantics;
- graph query contracts;
- graph versioning.

#### Not responsible for

- session lifecycle;
- learner mastery;
- assessment scoring;
- orchestration decisions;
- session persistence.

### 4.6 Retrieval Layer

#### Responsible for

- retrieving approved educational knowledge;
- retrieving evidence packages;
- preserving source references;
- enforcing retrieval-specific constraints;
- returning retrieval metadata.

#### Not responsible for

- owning Learning Session state;
- selecting the next node;
- mutating Student Model state;
- mutating Curriculum Graph state;
- controlling session lifecycle.

### 4.7 LLM Gateway

#### Responsible for

- model-provider abstraction;
- provider routing;
- request execution;
- model configuration;
- invocation telemetry;
- provider-specific error normalization;
- safety and execution controls for model access.

#### Not responsible for

- owning pedagogical authority;
- owning Learning Session lifecycle;
- persisting learner state;
- selecting the next node;
- directly applying session mutations.

---

## 5. Data Ownership Classification

AIGORA distinguishes five data classifications:

- owned;
- referenced;
- cached;
- derived;
- transient.

### 5.1 Owned by the Learning Session bounded context

The Learning Session bounded context owns:

- `LearningSessionId`;
- session status;
- session version;
- current node reference;
- current exercise reference;
- exercise-attempt identity;
- exercise-attempt lifecycle;
- session correlation metadata;
- command identities required for idempotency;
- event identities required for idempotency;
- session start timestamp;
- session completion timestamp;
- session interruption timestamp;
- session failure timestamp;
- terminal reason;
- session recovery checkpoints.

### 5.2 Referenced by the Learning Session bounded context

The Learning Session references, but does not own:

- `StudentId`;
- Student Model snapshot identity;
- Student Model snapshot version;
- `NodeId`;
- Curriculum Graph version;
- assessment result identity;
- assessment contract version;
- orchestration decision identity;
- retrieved-content identity;
- generated-content identity.

References must be represented through immutable identifiers or immutable versioned snapshots.

### 5.3 Derived by the Learning Session bounded context

The Learning Session may derive:

- whether a session command is legal;
- whether assessment may be requested;
- whether a pedagogical decision may be requested;
- whether a session reached a terminal state;
- session progress indicators derived only from owned session state.

Derived session data must not silently become a replacement for:

- Student Model mastery;
- Assessment Engine scoring;
- Tutor Orchestrator selection policies.

### 5.4 Cached by the Learning Session bounded context

The Learning Session may temporarily cache:

- immutable node display metadata;
- immutable assessment summaries;
- immutable orchestration decision summaries;
- immutable content references required for recovery.

Cached data must:

- identify its source;
- identify its source version;
- remain replaceable;
- never be treated as authoritative external state;
- never permit mutation of another bounded context.

### 5.5 Transient data

Transient data may include:

- transport metadata;
- timeout budgets;
- request-scoped tracing information;
- temporary retrieval payloads;
- temporary LLM generation payloads;
- non-persisted adapter diagnostics.

Transient data is not aggregate state unless a later ADR explicitly promotes it.

---

## 6. Command Ownership

### 6.1 Learning Session commands

Commands that change Learning Session state belong to the Learning Session application boundary.

Examples:

- `StartLearningSession`;
- `PresentExercise`;
- `CompleteExercise`;
- `ApplyAssessmentResult`;
- `ApplyOrchestrationDecision`;
- `CompleteLearningSession`;
- `InterruptLearningSession`;
- `FailLearningSession`.

The exact command contracts are governed by ADR-007 and the final lifecycle model in ADR-009.

### 6.2 Tutor Orchestrator commands

Tutor Orchestrator inputs represent decision requests, not session mutations.

Examples:

- `SelectNextNode`;
- `EvaluateProgression`;
- `DetermineCompletion`;
- `DetermineRegression`.

These operations return immutable decisions.

They do not directly change the `LearningSession` aggregate.

---

## 7. Event Ownership

### 7.1 Learning Session events

Events representing committed Learning Session facts belong to the Learning Session bounded context.

Examples:

- `LearningSessionCreated`;
- `LearningSessionStarted`;
- `ExercisePresented`;
- `ExerciseCompleted`;
- `AssessmentAccepted`;
- `OrchestrationDecisionApplied`;
- `LearningSessionCompleted`;
- `LearningSessionInterrupted`;
- `LearningSessionFailed`.

### 7.2 Tutor Orchestrator events

Events representing pedagogical decision processing belong to the Tutor Orchestrator.

Examples:

- `PoliciesExecuted`;
- `CandidatesGenerated`;
- `CandidatesRanked`;
- `NodeSelected`;
- `NoEligibleCandidateFound`;
- `CompletionSelected`;
- `RegressionSelected`.

### 7.3 Event ownership rule

An event is owned by the bounded context that owns the state change or decision fact it represents.

A component must not publish an event that claims another bounded context's authoritative state changed unless that change was committed by the owning bounded context.

Detailed event publication guarantees are defined by ADR-010.

---

## 8. Interaction Boundaries

### 8.1 Allowed synchronous interactions

The initial v0.3.1 implementation may use synchronous request/response boundaries for:

- Learning Session Engine → Assessment Engine;
- Learning Session Engine → Tutor Orchestrator;
- Tutor Orchestrator → Curriculum Graph;
- Tutor Orchestrator → Student Model;
- Tutor Orchestrator → Retrieval Layer;
- Tutor Orchestrator → LLM Gateway, only when explicitly permitted by policy.

Synchronous calls must:

- use explicit ports;
- use immutable contracts;
- propagate correlation identifiers;
- propagate causation identifiers when applicable;
- define timeout behavior;
- return typed failures;
- avoid distributed transactions;
- avoid direct persistence coupling.

### 8.2 Allowed asynchronous interactions

Session and pedagogical events may be published asynchronously.

Asynchronous boundaries must:

- use explicit event contracts;
- include event identity;
- include aggregate or decision version;
- include correlation metadata;
- support duplicate delivery;
- support idempotent consumers;
- define ordering expectations;
- avoid assuming exactly-once delivery.

Detailed asynchronous behavior is governed by ADR-010.

---

## 9. Prohibited Dependencies

The following dependencies are prohibited:

- Tutor Orchestrator directly mutating Learning Session state;
- Assessment Engine directly mutating Learning Session state;
- Student Model directly mutating Learning Session state;
- Curriculum Graph directly mutating Learning Session state;
- Learning Session Engine directly accessing another component's database;
- Tutor Orchestrator directly accessing Learning Session persistence;
- shared mutable entities across bounded contexts;
- shared database tables as integration contracts;
- bidirectional compile-time dependencies between bounded contexts;
- transport adapters mutating aggregate fields directly;
- persistence adapters bypassing aggregate invariants;
- LLM Gateway returning an authoritative session mutation;
- Curriculum Graph becoming aware of a concrete `LearningSession`;
- Tutor Orchestrator persisting a duplicate `LearningSession` aggregate;
- Assessment Engine selecting the next learning node;
- Learning Session Engine duplicating Tutor Orchestrator ranking logic.

---

## 10. Allowed Dependency Directions

The architecture permits the following logical dependency directions:

```text
Learning Session Engine
    → Assessment Engine port

Learning Session Engine
    → Tutor Orchestrator port

Tutor Orchestrator
    → Student Model port

Tutor Orchestrator
    → Curriculum Graph port

Tutor Orchestrator
    → Retrieval Layer port

Tutor Orchestrator
    → LLM Gateway port
```

At the code level, domain modules must not depend on infrastructure implementations.

Interaction must follow:

```text
application service
    → outbound port
    → adapter
    → external component contract
```

The following is forbidden:

```text
component A domain
    → component B adapter

component A
    → component B database

component A aggregate
    → component B aggregate
```

---

## 11. Consistency Boundary

The `LearningSession` aggregate is the consistency boundary for Learning Session state.

Inside this boundary:

- lifecycle invariants are strongly consistent;
- session version changes are atomic;
- exercise-attempt state changes are atomic with the session mutation;
- terminal-state transitions are atomic;
- session events are generated from committed aggregate changes.

Outside this boundary:

- assessment results are external references;
- Student Model state is external;
- Curriculum Graph state is external;
- orchestration decisions are external immutable results;
- cross-component updates may be eventually consistent.

The Learning Session Engine must not attempt to create a distributed transaction across these bounded contexts.

---

## 12. Boundary Violation Rules

An implementation proposal violates ADR-008 when it:

- assigns Learning Session mutation authority to more than one component;
- stores a second authoritative copy of session state;
- gives Tutor Orchestrator responsibility for session persistence;
- gives Learning Session Engine responsibility for candidate ranking;
- allows Assessment Engine to apply session transitions;
- shares persistence models across components;
- creates bidirectional component dependencies;
- bypasses explicit ports;
- allows external services to mutate the aggregate directly;
- treats cached external state as authoritative.

A violating proposal must be rejected or redesigned before implementation.

A superseding ADR is required to change these rules.

---

## 13. Alternatives Considered

### Alternative A — Tutor Orchestrator owns the complete Learning Session aggregate

#### Rejected

This would combine:

- session lifecycle;
- exercise execution;
- attempt state;
- assessment coordination;
- pedagogical decision-making.

It would weaken the established separation between deciding and executing.

It would also risk turning the Tutor Orchestrator into a broad workflow engine rather than a focused pedagogical decision component.

### Alternative B — Shared ownership between Tutor Orchestrator and Learning Session Engine

#### Rejected

Shared mutation authority would create:

- ambiguous invariants;
- concurrent writes;
- duplicate persistence;
- distributed consistency problems;
- unclear recovery authority;
- bidirectional dependencies.

An aggregate must have one authoritative owner.

### Alternative C — Student Model owns the session

#### Rejected

The Student Model owns durable learner knowledge state.

It does not own operational Learning Session execution.

Exercise attempts may contribute evidence to the Student Model, but this does not transfer lifecycle ownership.

### Alternative D — Assessment Engine owns progression after exercise completion

#### Rejected

The Assessment Engine produces evaluation evidence.

It does not own the broader learning-session lifecycle or pedagogical node selection.

### Alternative E — Learning Session Engine owns the aggregate and requests decisions from Tutor Orchestrator

#### Accepted

This preserves:

- one aggregate owner;
- separation between decision and execution;
- bounded-context independence;
- explicit contracts;
- replaceable integrations;
- deterministic orchestration;
- auditability;
- incremental evolution toward asynchronous flows.

---

## 14. Consequences

### 14.1 Positive consequences

- one component owns all Learning Session invariants;
- session state and decision state remain separate;
- the Tutor Orchestrator retains a focused responsibility;
- external state remains referenced and versioned;
- persistence boundaries are explicit;
- recovery ownership is unambiguous;
- testing can isolate each bounded context;
- future asynchronous delivery remains possible;
- shared-database integration is prevented;
- decision traceability remains independent from session persistence.

### 14.2 Negative consequences

- the Learning Session Engine coordinates multiple component calls;
- more explicit request and result mapping is required;
- correlation and causation metadata must cross component boundaries;
- orchestration decisions may become stale before application;
- local development requires fakes for several outbound ports;
- asynchronous evolution will require durable delivery mechanisms.

### 14.3 Accepted trade-off

AIGORA accepts additional explicit contracts and coordination complexity in exchange for:

- single ownership;
- deterministic behavior;
- clear bounded contexts;
- independent evolution;
- stronger auditability;
- safer recovery;
- reduced architectural ambiguity.

---

## 15. Follow-up Actions

### Required for v0.3.1

1. Create ADR-009 defining the `LearningSession` aggregate and lifecycle.
2. Create ADR-010 defining event publication and consistency boundaries.
3. Create ADR-011 defining Learning Session persistence and recovery.
4. Implement Learning Session identity and lifecycle value objects.
5. Implement the Learning Session status model.
6. Implement the `LearningSession` aggregate.
7. Implement `ExerciseAttempt`.
8. Define immutable orchestration request and result contracts.
9. Define Learning Session repository port.
10. Define event publication and decision-trace ports.
11. Update component ownership documentation.
12. Update the responsibility matrix.
13. Update architectural responsibility boundaries.
14. Update Learning Session Engine documentation.
15. Add architecture tests for forbidden dependencies.
16. Add traceability from implementation issues to ADR-008.

### Required task interpretation

Any task description that says the complete Learning Session lifecycle is implemented inside the Tutor Orchestrator must be revised or interpreted as:

- Learning Session lifecycle belongs to the Learning Session bounded context;
- pedagogical decision-making is delegated to the Tutor Orchestrator.

---

## 16. Compliance Rules

An implementation complies with ADR-008 only when:

- the Learning Session Engine is the sole authoritative owner of the `LearningSession` aggregate;
- only Learning Session application use cases mutate the aggregate;
- Tutor Orchestrator interactions use immutable contracts;
- external component data is referenced by identity or version;
- no shared database integration is introduced;
- no bidirectional component dependency is introduced;
- session mutations do not require direct external persistence access;
- decision and execution responsibilities remain separated;
- external component failures are mapped through explicit contracts;
- cached data is not treated as authoritative.

Any pull request violating these rules must be rejected or accompanied by a superseding ADR.

---

## 17. Milestone Linkage

ADR-008 enables the v0.3.1 milestone by resolving the ownership ambiguity that blocks:

- aggregate design;
- lifecycle definition;
- event contracts;
- repository contracts;
- command and result contracts;
- orchestration integration;
- persistence boundaries;
- recovery design;
- architecture tests;
- auditability;
- observability.

The milestone remains dependent on ADR-009, ADR-010, and ADR-011 for lifecycle, event consistency, persistence, and recovery details.

---

## 18. Decision Summary

The final architectural responsibility is:

```text
Learning Session Engine
    owns and mutates LearningSession

Tutor Orchestrator
    produces pedagogical decisions

Assessment Engine
    produces assessment results

Student Model
    owns learner knowledge state

Curriculum Graph
    owns curriculum topology

Retrieval Layer
    owns retrieval behavior and evidence

LLM Gateway
    owns model invocation execution
```

There is exactly one authoritative owner of Learning Session state:

```text
Learning Session Engine
```
