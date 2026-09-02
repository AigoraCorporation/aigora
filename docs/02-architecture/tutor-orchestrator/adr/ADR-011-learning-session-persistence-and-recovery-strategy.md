# ADR-011 — Learning Session Persistence and Recovery Strategy

- **Status:** Accepted
- **Date:** 2026-08-02
- **Decision Owners:** AIGORA Architecture
- **Milestone:** v0.3.1 — Learning Session Orchestration
- **Supersedes:** None
- **Superseded by:** None
- **Related ADRs:**
  - ADR-006 — Java Layered Architecture
  - ADR-007 — Command-Result Application Contracts
  - ADR-008 — Learning Session Ownership and Bounded-Context Boundaries
  - ADR-009 — Learning Session Aggregate and Lifecycle Model
  - ADR-010 — Event Publication and Consistency Boundaries

---

## 1. Context

The Learning Session Engine is the authoritative owner of the `LearningSession` aggregate.

ADR-008 establishes ownership and bounded-context boundaries. ADR-009 defines the aggregate, lifecycle states, invariants, versioning semantics, and legal transitions. ADR-010 defines event publication, consistency boundaries, idempotency expectations, and the Transactional Outbox Pattern.

The remaining architectural question is how Learning Session state is persisted, rehydrated, recovered, and protected against concurrent or duplicate execution.

A Learning Session is operationally important because it represents the active progression of one learner through a pedagogical flow. Loss, duplication, corruption, or inconsistent recovery may cause:

- duplicated exercise attempts;
- repeated assessment processing;
- application of the same orchestration decision more than once;
- invalid lifecycle transitions;
- stale state overwriting newer state;
- divergence between persisted state and published events;
- unrecoverable sessions after application failure;
- incorrect Student Model updates;
- incomplete decision traceability.

This ADR defines the persistence and recovery strategy for the Learning Session bounded context. It covers repository boundaries, aggregate persistence, optimistic concurrency, transaction boundaries, rehydration, command idempotency, Outbox integration, failure recovery, recovery checkpoints, persistence model separation, snapshot strategy, operational repair, and prohibited implementation patterns.

This ADR does not select a specific database technology. Technology-specific mappings belong to infrastructure documentation and implementation tasks.

---

## 2. Decision

AIGORA adopts a **state-based aggregate persistence model with optimistic concurrency control, command idempotency, transactional Outbox integration, and explicit recovery semantics** for the `LearningSession` aggregate.

The persistence model follows these principles:

1. `LearningSession` is persisted as one authoritative aggregate state.
2. Every successful mutation increments the aggregate version.
3. Saves use optimistic concurrency.
4. Aggregate state and Outbox records are committed in the same local transaction.
5. Rehydration restores state without executing business transitions or emitting new events.
6. Duplicate commands are detected before mutation.
7. Recovery resumes from the last successfully committed state.
8. Cross-bounded-context transactions are prohibited.
9. Repository contracts remain independent from database technology.
10. Event Sourcing is not adopted for v0.3.1.

---

## 3. Persistence Model

### 3.1 Authoritative state

The authoritative state of a Learning Session is the latest successfully committed representation of the `LearningSession` aggregate.

The persisted aggregate includes all state required to preserve its invariants and continue execution, including:

- `LearningSessionId`;
- `StudentId`;
- current lifecycle status;
- current aggregate version;
- current node reference;
- current exercise reference;
- exercise attempts;
- accepted assessment references;
- applied orchestration decision references;
- terminal reason;
- creation, activation, completion, interruption, and failure timestamps;
- idempotency metadata required by the aggregate;
- recovery metadata explicitly owned by the Learning Session bounded context.

External component state is not embedded as authoritative mutable state. References to external bounded contexts must remain immutable and version-aware where applicable.

### 3.2 State-based persistence

AIGORA persists the current aggregate state. The system does not reconstruct the aggregate exclusively by replaying all historical domain events.

```text
Load latest persisted aggregate state
    ↓
Rehydrate LearningSession
    ↓
Execute command
    ↓
Validate invariants
    ↓
Persist new aggregate state
```

Historical events remain valuable for auditability and integration, but they are not the only source required to rebuild operational state.

### 3.3 Why Event Sourcing is not adopted

Event Sourcing was considered but is not adopted for v0.3.1 because:

- the Learning Session lifecycle does not yet require event-stream reconstruction as the primary storage model;
- operational simplicity is preferred for the first production-grade implementation;
- event schema evolution would become persistence schema evolution;
- replay semantics would be more complex;
- projections and snapshots would become mandatory infrastructure;
- the team can preserve auditability through committed events and decision traces without making the event stream the sole source of truth.

Event Sourcing may be reconsidered through a future ADR if operational or analytical requirements justify the additional complexity.

---

## 4. Repository Boundary

The `LearningSessionRepository` is an outbound port owned by the Learning Session application boundary.

The domain model must not depend on JPA, Hibernate, JDBC, SQL, Neo4j, MongoDB, Redis, serialization libraries, or database-specific annotations.

The repository exposes domain-oriented operations.

```java
public interface LearningSessionRepository {

    Optional<LearningSession> findById(LearningSessionId sessionId);

    void insert(LearningSession session);

    void update(
        LearningSession session,
        SessionVersion expectedVersion
    );
}
```

The final Java contract may introduce explicit result types or typed exceptions according to the project error model.

---

## 5. Repository Responsibilities

The repository is responsible for:

- loading persisted Learning Session state;
- reconstructing the aggregate through approved rehydration mechanisms;
- inserting new aggregates;
- updating existing aggregates;
- enforcing optimistic concurrency;
- persisting aggregate-owned child entities;
- participating in the local transaction;
- preserving aggregate version;
- preserving owned timestamps;
- mapping persistence errors into typed infrastructure failures.

The repository is not responsible for:

- deciding lifecycle transitions;
- applying domain rules;
- selecting the next pedagogical node;
- evaluating assessments;
- generating new domain events;
- invoking the Tutor Orchestrator;
- publishing integration events;
- mutating the aggregate after persistence;
- bypassing aggregate invariants.

---

## 6. Aggregate Boundary and Atomicity

The `LearningSession` aggregate is the atomic persistence boundary.

A successful save must atomically persist:

- the aggregate root;
- aggregate-owned `ExerciseAttempt` entities;
- aggregate-owned value objects;
- the new aggregate version;
- Outbox records produced by the same committed mutation;
- command-processing metadata required for idempotency, when stored transactionally with the aggregate.

The persistence adapter must not partially commit aggregate-owned state.

```text
LearningSession status updated
    ✓

ExerciseAttempt not updated
    ✗
```

A transaction must either commit the entire aggregate mutation or commit nothing.

---

## 7. Aggregate Versioning

Every `LearningSession` has a monotonically increasing version.

Recommended semantics:

```text
New aggregate before first persistence
Version = 0

After initial insert
Version = 1

After first successful mutation
Version = 2
```

The exact initial numerical representation may vary, but the semantics must remain consistent throughout the system.

The version represents the number of successfully committed aggregate states. It must not represent event schema version, Curriculum Graph version, Student Model version, or number of attempts.

---

## 8. Optimistic Concurrency Control

AIGORA uses optimistic concurrency to prevent stale writes.

Every update includes the version originally loaded by the application.

```sql
UPDATE learning_session
SET
    status = ?,
    aggregate_version = ?
WHERE
    session_id = ?
    AND aggregate_version = ?;
```

If no record is updated, the persistence adapter must report a concurrency conflict.

```text
Request A loads version 7
Request B loads version 7

Request A commits version 8

Request B attempts to commit using expected version 7

Result:
Concurrency conflict
```

Request B must not overwrite version 8.

---

## 9. Concurrency Conflict Handling

A concurrency conflict is not automatically a system failure.

The application use case must classify the command and determine whether retry is safe.

Possible actions:

1. return a typed conflict result;
2. reload the latest aggregate;
3. re-evaluate command idempotency;
4. retry only when the command remains semantically valid;
5. reject the command when the state has advanced incompatibly.

Blind retries are prohibited.

A duplicate `CompleteExercise` command may become an idempotent success after reload. A stale `PresentExercise` command may need to be rejected because another exercise is already active.

---

## 10. Transaction Boundary

The application use case defines the business transaction boundary.

```text
Receive command
    ↓
Validate command envelope
    ↓
Check command idempotency
    ↓
Load aggregate
    ↓
Execute aggregate behavior
    ↓
Collect pending domain events
    ↓
Begin local transaction
    ↓
Persist aggregate
    +
Persist Outbox records
    +
Persist command-processing result
    ↓
Commit
    ↓
Return application result
```

The local transaction must not include remote network calls.

---

## 11. Remote Calls and Transactions

Calls to the Assessment Engine, Tutor Orchestrator, Student Model, Curriculum Graph, Retrieval Layer, LLM Gateway, or message broker must occur outside the database transaction.

Holding a database transaction open during remote calls is prohibited.

```text
1. Persist ExerciseCompleted transition
2. Commit
3. Publish event through Outbox
4. Assessment processing occurs
5. Receive assessment result
6. Load latest session
7. Apply result
8. Persist new version and Outbox events
```

This approach accepts eventual consistency across bounded contexts.

---

## 12. Transactional Outbox Integration

ADR-010 requires durable integration-event publication through the Transactional Outbox Pattern.

For every aggregate mutation that produces publishable events:

```text
Aggregate state
    +
Outbox records
```

must be persisted in the same local transaction.

This guarantees that no committed aggregate change loses its corresponding integration event and no integration event becomes visible for a state that failed to commit.

---

## 13. Outbox Record

A conceptual Outbox record contains:

- Outbox record ID;
- Event ID;
- Event type;
- Aggregate ID;
- Aggregate type;
- Aggregate version;
- Correlation ID;
- Causation ID;
- Event schema version;
- Producer;
- OccurredAt;
- serialized payload;
- publication status;
- publication attempts;
- next-attempt timestamp;
- published timestamp;
- last failure reason.

The exact storage schema belongs to infrastructure implementation. The Outbox payload must preserve the immutable event envelope defined by ADR-010.

---

## 14. Outbox Publication Semantics

The Outbox publisher:

1. reads unpublished records;
2. publishes them to the configured event transport;
3. records publication success;
4. retries transient failures;
5. surfaces permanently failing records operationally.

The architecture assumes at-least-once publication.

A crash may occur after broker acceptance but before the Outbox record is marked as published. Therefore, duplicate publication is possible and consumers must remain idempotent.

---

## 15. Rehydration

Rehydration reconstructs a `LearningSession` from persisted state.

Rehydration must restore aggregate identity, lifecycle status, aggregate version, owned entities and value objects, timestamps, external references, idempotency metadata, and recovery metadata.

Rehydration must not:

- execute lifecycle transitions;
- invoke public aggregate commands;
- increment aggregate version;
- generate new domain events;
- publish events;
- invoke external components;
- recalculate historical decisions;
- rewrite timestamps.

---

## 16. Rehydration API

The aggregate should expose a controlled rehydration mechanism.

```java
public static LearningSession rehydrate(LearningSessionState state) {
    // Restore previously validated committed state.
}
```

The state object should be immutable and the rehydration mechanism should have restricted visibility where practical.

---

## 17. Persistence Validation During Rehydration

Persisted state is trusted as previously committed state, but structural corruption must still be detected.

Examples:

- unknown lifecycle status;
- missing aggregate identifier;
- negative aggregate version;
- duplicated attempt identifiers;
- terminal session without required terminal metadata;
- incompatible persistence schema version.

Detected corruption must produce an explicit recovery failure. The repository must not silently repair corrupted state.

---

## 18. Command Idempotency

Every externally retryable mutation command must have a unique `CommandId`.

Examples include `CompleteExercise`, `ApplyAssessmentResult`, `ApplyOrchestrationDecision`, `InterruptLearningSession`, and `FailLearningSession`.

The same `CommandId` must not cause more than one aggregate mutation.

---

## 19. Idempotency Result Semantics

When a duplicate command is received, the application should return the previously committed result when available.

```text
CommandId C-123 received
    ↓
Command processed successfully
    ↓
Result R-456 persisted

CommandId C-123 received again
    ↓
No new aggregate mutation
    ↓
Return Result R-456
```

A duplicate command with the same `CommandId` but different semantic payload is invalid and must be rejected.

---

## 20. Processed Command Storage

Command idempotency metadata may be stored inside aggregate-owned persistence, in a dedicated idempotency table within the same bounded-context database, or through a bounded command-result store.

Regardless of representation, the command result and aggregate mutation must commit atomically when the command changes state.

Recommended fields:

- CommandId;
- command type;
- aggregate ID;
- request fingerprint;
- processing status;
- result payload or result reference;
- aggregate version after processing;
- processed timestamp.

---

## 21. Request Fingerprint

The system should compute a deterministic fingerprint for commands that require duplicate-payload validation.

Inputs may include command type, Learning Session ID, relevant business payload, external result ID, and expected session version.

The fingerprint must exclude volatile transport metadata.

A repeated `CommandId` with a different fingerprint indicates invalid reuse or a client defect.

---

## 22. Recovery Model

Recovery always begins from the last successfully committed aggregate state.

There is no recovery from in-memory state that was never committed.

```text
Restart application
    ↓
Load latest committed LearningSession
    ↓
Inspect lifecycle and recovery metadata
    ↓
Inspect pending Outbox records
    ↓
Resume eligible workflow
```

The system must never infer that an uncommitted transition succeeded.

---

## 23. Recovery Checkpoints

The aggregate lifecycle itself is the primary recovery checkpoint.

Recovery-sensitive states include `ACTIVE`, `AWAITING_ASSESSMENT`, `PROCESSING_DECISION`, and terminal states.

A session in `AWAITING_ASSESSMENT` indicates that exercise completion was committed and assessment processing remains outstanding or incomplete.

A session in `PROCESSING_DECISION` indicates that required assessment evidence was accepted and a pedagogical decision remains outstanding or unapplied.

---

## 24. Recovery by Lifecycle State

### 24.1 `CREATED`

Allow session start or expire/cancel according to future product policy.

### 24.2 `ACTIVE`

Restore the current exercise and continue learner interaction without duplicating presentation side effects.

### 24.3 `AWAITING_ASSESSMENT`

Verify whether an assessment result has already been accepted, replay or reissue the assessment request using the same idempotency identity, and avoid creating a second assessment for the same attempt.

### 24.4 `PROCESSING_DECISION`

Verify whether a decision has already been applied, recover or retry the orchestration request using stable request identity, and apply only when the expected session version remains valid.

### 24.5 Terminal states

For `COMPLETED`, `INTERRUPTED`, and `FAILED`, no normal lifecycle mutation is resumed. Only read, audit, repair, or explicitly authorized administrative operations are allowed.

---

## 25. Recovery Coordinator

Workflow recovery belongs to the Learning Session application layer.

A recovery coordinator may:

- query sessions in recoverable states;
- load the aggregate;
- evaluate persisted recovery metadata;
- invoke application use cases;
- reuse stable command and request identities;
- record operational metrics.

It must not mutate persistence directly, bypass the aggregate, fabricate external results, change terminal states silently, or execute unbounded retries.

---

## 26. Stable External Request Identity

Requests to external components should carry stable identities, such as `AssessmentRequestId` and `OrchestrationRequestId`.

A retried assessment request for the same exercise attempt must reuse the original request identity.

A retried orchestration request for the same decision point must reuse the original request identity unless a new aggregate version or new evidence explicitly creates a new decision request.

---

## 27. Assessment Recovery

When recovering a session awaiting assessment:

1. load the latest aggregate;
2. identify the completed attempt;
3. identify the persisted assessment request reference;
4. query or retry through the Assessment Engine contract;
5. require idempotent Assessment Engine semantics;
6. apply a result only if it has not already been accepted;
7. persist the new aggregate version and Outbox records atomically.

A different assessment result for an already accepted assessment identity must be treated as a consistency violation.

---

## 28. Orchestration Decision Recovery

When recovering a session processing a pedagogical decision:

1. load the latest aggregate;
2. restore accepted assessment reference;
3. restore Student Model and Curriculum Graph version references when required;
4. identify the orchestration request identity;
5. query or retry the Tutor Orchestrator;
6. validate the returned decision identity and evidence;
7. verify expected aggregate version;
8. apply the decision once;
9. persist the aggregate and Outbox records atomically.

The same `OrchestrationDecisionId` must not be applied twice.

---

## 29. Crash Scenarios

### 29.1 Crash before transaction commit

No aggregate mutation, Outbox event, or command result is committed. The command may be retried using the same `CommandId`.

### 29.2 Crash after transaction commit but before response

The aggregate mutation, Outbox event, and command result are committed, but the caller may believe the request failed. A retry with the same `CommandId` returns the previously committed result without executing again.

### 29.3 Crash after broker publish but before Outbox acknowledgment

The event may be delivered more than once. The Outbox publisher may republish and consumers must detect duplicate `EventId` values.

### 29.4 Crash during remote request

The remote component may or may not have processed the request. Recovery must retry using the same external request identity and depend on idempotent external contracts.

---

## 30. Timeout Semantics

A timeout means the result is unknown. It does not prove failure.

After a timeout the application must not assume the external operation failed, generate a second semantic request with a new identity, or apply compensating state blindly.

The next action must use stable request identity and query-or-retry semantics.

---

## 31. Partial Commit Prevention

The local persistence implementation must guarantee atomicity for aggregate root state, child entity state, command idempotency state, and Outbox records.

A database transaction is required where the selected persistence technology supports transactions.

If a technology cannot provide the required atomicity, it must not be used for the authoritative Learning Session store without a superseding ADR.

---

## 32. Snapshot Strategy

Because v0.3.1 uses state-based persistence, the latest aggregate state already functions as the operational snapshot.

Additional event-stream snapshots are not required.

Future snapshot mechanisms may be introduced for large attempt histories, long-running sessions, analytical reconstruction, or migration optimization. They must not alter aggregate semantics.

---

## 33. Exercise Attempt Persistence

`ExerciseAttempt` is aggregate-owned state.

Its persistence must be controlled through the `LearningSession` repository.

A separate `ExerciseAttemptRepository` must not be introduced if it permits independent mutation outside the aggregate.

Read-only projections may exist for reporting or analytics, but they are not authoritative mutation paths.

---

## 34. Persistence Mapping

The infrastructure layer may use a persistence representation different from the domain object graph.

```text
Domain
LearningSession
ExerciseAttempt
Value Objects

        ↕ Mapper

Persistence
LearningSessionRecord
ExerciseAttemptRecord
OutboxRecord
ProcessedCommandRecord
```

Persistence entities must not leak into the domain or application API.

---

## 35. Schema Versioning

Persisted aggregate representations should include a persistence schema version when backward-compatible mapping cannot be guaranteed implicitly.

The persistence schema version is distinct from aggregate version, event schema version, and command contract version.

Migrations must preserve valid historical sessions and must not reinterpret past business facts without explicit architectural review.

---

## 36. Deletion and Retention

Physical deletion of Learning Sessions is not part of normal domain behavior.

Terminal sessions may be retained according to legal, privacy, audit, and operational requirements.

Deletion, anonymization, and archival require a separate data-retention and privacy decision.

The repository contract should not expose unrestricted `delete()` as a normal domain operation.

---

## 37. Backup and Restore

Database backup and restore are infrastructure responsibilities.

Restored data must preserve aggregate version, Outbox state, processed-command state, external request references, decision references, timestamps, and correlation/causation metadata.

Restoring aggregate state without corresponding Outbox and idempotency state may produce duplicate or lost processing.

---

## 38. Operational Repair

Automatic recovery must not silently modify corrupted business state.

Operational repair requires explicit authorization, an audit record, a reason, operator or system identity, before-and-after evidence, a correlation identifier, and a controlled repair application service.

Direct database updates are prohibited except under documented emergency procedures.

---

## 39. Failure Classification

Persistence and recovery failures are classified as:

### 39.1 Not Found

The requested Learning Session does not exist.

### 39.2 Concurrency Conflict

The expected aggregate version no longer matches.

### 39.3 Duplicate Command

The command was already processed and may be returned as idempotent success when payload matches.

### 39.4 Command Identity Conflict

The same `CommandId` was reused with a different payload.

### 39.5 Persistence Unavailable

The authoritative store is temporarily unavailable.

### 39.6 Persistence Corruption

Persisted state cannot be safely rehydrated.

### 39.7 Outbox Publication Delayed

Aggregate state is committed, but external publication remains pending.

### 39.8 Recovery Exhausted

Automatic recovery exceeded its configured retry or time boundary.

Each failure must map to a typed application or infrastructure error.

---

## 40. Retry Rules

Retry may be appropriate for temporary database unavailability, transient transaction failure, retryable optimistic conflict after semantic re-evaluation, temporary Outbox publication failure, and timeout with stable external request identity.

Retry is not appropriate for invalid lifecycle transition, corrupted persisted state, command identity conflict, unsupported persistence schema, or unauthorized repair request.

Retry policies belong to infrastructure and application coordination, not the aggregate.

---

## 41. Read Models

Read models may be built for dashboards, learner progress views, session monitoring, audit search, and operational recovery queues.

Read models are eventually consistent and must not become authoritative mutation sources.

Commands must load authoritative aggregate state through the repository.

---

## 42. Caching

Caching authoritative Learning Session state is optional and not required for v0.3.1.

If introduced, a cache must remain non-authoritative, include aggregate version, support invalidation, tolerate stale entries, never bypass optimistic concurrency, and never become the sole source used for recovery.

Write-behind caching is prohibited for authoritative session mutations.

---

## 43. Repository Port Example

A richer conceptual Java contract may look like:

```java
public interface LearningSessionRepository {

    Optional<LearningSession> findById(LearningSessionId sessionId);

    InsertResult insert(
        LearningSession session,
        Collection<OutboxEvent> outboxEvents,
        ProcessedCommand processedCommand
    );

    UpdateResult update(
        LearningSession session,
        SessionVersion expectedVersion,
        Collection<OutboxEvent> outboxEvents,
        ProcessedCommand processedCommand
    );
}
```

This shape is illustrative, not mandatory. The final design may instead use a Unit of Work abstraction.

---

## 44. Unit of Work Alternative

A bounded-context Unit of Work may coordinate repository save, Outbox append, processed-command append, and transaction commit.

```java
public interface LearningSessionUnitOfWork {

    LearningSessionRepository sessions();

    OutboxRepository outbox();

    ProcessedCommandRepository processedCommands();

    void commit();
}
```

This is acceptable only if transaction ownership remains explicit, domain code remains infrastructure-independent, partial commits are impossible, and the Unit of Work does not become a generic cross-bounded-context transaction manager.

---

## 45. Prohibited Patterns

The following patterns are prohibited:

- direct database access from the aggregate;
- persistence annotations controlling domain behavior;
- remote calls inside the local database transaction;
- shared transactions across bounded contexts;
- last-write-wins updates without version checking;
- silently ignoring optimistic concurrency conflicts;
- publishing integration events before commit;
- persisting aggregate state without matching Outbox records;
- generating new domain events during rehydration;
- calling public mutation methods to restore state;
- independent mutation of `ExerciseAttempt`;
- unrestricted repository deletion;
- direct database repair as normal application behavior;
- new external request IDs on timeout retries;
- using logs as the only recovery record;
- assuming exactly-once broker delivery.

---

## 46. Architecture Tests

The codebase should include automated tests that verify:

- domain modules do not depend on persistence frameworks;
- repository implementations reside in infrastructure modules;
- aggregate mutation is not exposed through persistence records;
- `ExerciseAttempt` has no independent mutation repository;
- Outbox persistence participates in the same local transaction;
- optimistic concurrency is enforced;
- rehydration emits no events;
- duplicate commands do not increment aggregate version;
- duplicate decisions are not applied twice;
- remote ports are not called from transactional persistence adapters;
- read models are not used as command-side repositories.

---

## 47. Required Test Scenarios

### Aggregate persistence

- create and insert a new session;
- load and rehydrate a session;
- update a session;
- persist child attempts atomically;
- preserve value objects;
- preserve terminal metadata.

### Concurrency

- two commands load the same version;
- first update succeeds;
- second update fails with a typed conflict;
- reload and semantic retry behavior is tested.

### Idempotency

- same command and same payload returns previous result;
- same command ID and different payload is rejected;
- duplicate command does not emit new events;
- duplicate command does not increment version.

### Outbox

- aggregate and Outbox commit together;
- aggregate rollback removes pending Outbox changes;
- publisher retry does not alter aggregate state;
- duplicate publication preserves EventId.

### Recovery

- crash before commit;
- crash after commit before response;
- recovery from `AWAITING_ASSESSMENT`;
- recovery from `PROCESSING_DECISION`;
- repeated external response;
- conflicting external response;
- terminal state is not resumed.

### Rehydration

- no lifecycle method is called;
- no domain event is generated;
- version remains unchanged;
- corrupted persistence representation fails explicitly.

---

## 48. Observability

Recommended metrics:

- repository load latency;
- repository save latency;
- transaction failure count;
- optimistic concurrency conflict count;
- duplicate command count;
- command identity conflict count;
- Outbox pending count;
- oldest pending Outbox age;
- Outbox retry count;
- recovery candidate count;
- recovery success count;
- recovery exhausted count;
- corrupted-state count.

Recommended trace attributes:

- `learning_session_id`;
- `aggregate_version`;
- `expected_version`;
- `command_id`;
- `correlation_id`;
- `causation_id`;
- `assessment_request_id`;
- `orchestration_request_id`;
- `outbox_event_count`;
- `recovery_state`.

Sensitive learner data must not be included in telemetry.

---

## 49. Security and Privacy

Persistence must follow least-privilege access.

The Learning Session storage credential must not provide access to unrelated bounded-context databases.

Sensitive payloads must be protected according to platform security standards.

Event and persistence payloads should avoid unnecessary personal information.

Recovery and repair operations require stronger authorization than ordinary session processing.

---

## 50. Alternatives Considered

### Alternative A — Last-write-wins persistence

**Rejected.** It allows stale requests to overwrite newer committed state and may violate lifecycle invariants.

### Alternative B — Pessimistic locking for the entire workflow

**Rejected.** Long-lived locks reduce scalability and are incompatible with workflows that include remote calls.

### Alternative C — Event Sourcing as the primary persistence model

**Rejected for v0.3.1.** It introduces additional operational and schema-evolution complexity that is not currently necessary.

### Alternative D — Aggregate persistence without command idempotency

**Rejected.** Retries after timeouts or crashes could apply the same business mutation more than once.

### Alternative E — Publish events directly after database commit without Outbox

**Rejected.** A crash between commit and publication could permanently lose integration events.

### Alternative F — State-based persistence with optimistic concurrency, idempotency, and Transactional Outbox

**Accepted.** It provides strong aggregate consistency, recoverability, and reliable event publication without introducing distributed transactions or full Event Sourcing.

---

## 51. Consequences

### 51.1 Positive consequences

- stale writes are detected;
- duplicate commands are safe;
- aggregate and Outbox remain consistent;
- process crashes are recoverable;
- external retries use stable identities;
- recovery ownership is explicit;
- database technology remains replaceable;
- domain code remains persistence-independent;
- auditability is preserved;
- eventual consistency is handled intentionally.

### 51.2 Negative consequences

- additional persistence records are required;
- idempotency results require storage;
- Outbox infrastructure must be operated;
- recovery coordination adds application complexity;
- optimistic conflicts require semantic handling;
- persistence migrations must preserve historical sessions;
- more integration and failure tests are required.

### 51.3 Accepted trade-off

AIGORA accepts additional persistence and recovery complexity in exchange for deterministic state transitions, reliable event publication, explicit failure semantics, and safe distributed workflow execution.

---

## 52. Follow-up Actions

Required implementation tasks for v0.3.1:

1. Define `LearningSessionRepository` port.
2. Define repository result and error contracts.
3. Define `SessionVersion`.
4. Define controlled aggregate rehydration.
5. Define persistence-state mapping.
6. Define `CommandId`.
7. Define processed-command storage contract.
8. Define request fingerprint strategy.
9. Define Outbox record contract.
10. Implement transactional aggregate and Outbox persistence.
11. Implement optimistic concurrency.
12. Implement duplicate-command handling.
13. Implement recovery coordinator.
14. Implement recovery for `AWAITING_ASSESSMENT`.
15. Implement recovery for `PROCESSING_DECISION`.
16. Add persistence migrations.
17. Add architecture tests.
18. Add transaction integration tests.
19. Add crash-recovery tests.
20. Add persistence and recovery observability.
21. Document operational repair procedures.
22. Document backup and restore consistency requirements.

---

## 53. Compliance Rules

An implementation complies with ADR-011 only when:

- `LearningSession` has one authoritative persisted state;
- updates enforce optimistic concurrency;
- aggregate version increases only after successful mutation;
- aggregate state and Outbox records commit atomically;
- duplicate commands do not repeat mutations;
- the same command ID with different payload is rejected;
- rehydration does not generate events;
- remote calls do not occur inside local database transactions;
- recovery starts from the last committed state;
- external retries reuse stable request identities;
- child entities cannot be independently mutated;
- persistence technology does not leak into the domain;
- read models remain non-authoritative;
- direct database repair is not a normal application path;
- failures are represented through typed contracts.

Any violation requires redesign or a superseding ADR.

---

## 54. Milestone Linkage

ADR-011 completes the foundational architectural decision sequence for v0.3.1:

```text
ADR-008
Ownership and bounded contexts

    ↓

ADR-009
Aggregate and lifecycle

    ↓

ADR-010
Event publication and consistency

    ↓

ADR-011
Persistence and recovery
```

This ADR enables implementation of Learning Session value objects, aggregate versioning, the `LearningSession` aggregate, `ExerciseAttempt`, domain events, command-result contracts, repository port, persistence adapter, Outbox adapter, recovery coordinator, and concurrency/idempotency/crash-recovery tests.

---

## 55. Decision Summary

AIGORA persists `LearningSession` using state-based aggregate persistence.

```text
Command
    ↓
Idempotency check
    ↓
Load authoritative aggregate
    ↓
Execute domain behavior
    ↓
Validate invariants
    ↓
Local transaction
    ├── Persist aggregate state
    ├── Persist processed command result
    └── Persist Outbox records
    ↓
Commit
    ↓
Return result
    ↓
Publish integration events asynchronously
```

The official recovery flow is:

```text
Application restart or recovery scan
    ↓
Load last committed aggregate state
    ↓
Inspect lifecycle and recovery metadata
    ↓
Reuse stable external request identity
    ↓
Resume through normal application use cases
    ↓
Persist new aggregate version and Outbox records
```

Core decisions:

- state-based persistence;
- optimistic concurrency;
- command idempotency;
- Transactional Outbox;
- controlled rehydration;
- no remote calls inside database transactions;
- no distributed transactions;
- no Event Sourcing for v0.3.1;
- recovery from the last committed state;
- stable request identities for uncertain remote outcomes.

---

## 56. Final Architectural Statement

ADR-011 establishes the authoritative persistence and recovery strategy for the AIGORA Learning Session bounded context.

The Learning Session Engine must preserve aggregate invariants, concurrency safety, idempotency, reliable event publication, and recoverability through explicit domain and application contracts.

No implementation may trade these guarantees for convenience through last-write-wins persistence, direct event publication, shared databases, distributed transactions, or uncontrolled state repair.

Until superseded, ADR-011 is the authoritative reference for Learning Session persistence, concurrency, idempotency, and recovery within AIGORA.
