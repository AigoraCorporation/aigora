# Student Model

This document defines the structure, computation model, and
operational constraints of the AIGORA Student Model.

The Student Model is the persistent representation of the learner.
It is the memory of the system, the foundation of adaptive decisions,
and the property of the student it represents.

This document is a companion to the
[Curriculum Graph](curriculum-graph.md) and
[Tutor Orchestrator](tutor-orchestrator.md).

---

# Design Principle

Mastery is not assigned. It is computed.

The Student Model does not store mastery levels as mutable fields
to be incremented after each interaction. It stores **evidence** —
the demonstrated performance record from which mastery is derived
at any point in time.

This distinction is foundational:

> An assigned mastery level reflects what the system *decided*.
> A computed mastery level reflects what the student *demonstrated*.

The graph provides the structural context for what mastery means.
The student provides the evidence of whether they have reached it.
The Student Model holds the evidence and exposes the computation.

---

# Responsibilities

The Student Model is responsible for:

- Storing all evidence of student performance against canonical nodes
- Computing mastery levels on demand from evidence and graph structure
- Tracking error patterns and misconception persistence
- Maintaining recency signals for evidence weighting
- Providing session reconstruction context to the orchestrator
- Projecting mastery state through a curriculum profile to produce readiness scores
- Enforcing write authority — only the Assessment Engine and orchestrator may write

---

# Evidence Store

The Student Model is an **evidence store**.

Every meaningful student interaction produces evidence.
Evidence is stored against canonical node ids and is never
modified after being written — it accumulates over time.

## Evidence Record

Each evidence record captures a single demonstrated performance event.

| Field | Description |
|---|---|
| **id** | Unique record identifier |
| **node\_id** | Canonical node the evidence relates to |
| **timestamp** | When the interaction occurred |
| **exercise\_id** | The exercise that produced this evidence |
| **outcome** | Correct, incorrect, or partial |
| **hint\_usage** | Number and type of hints used |
| **time\_taken** | Time from exercise presentation to response |
| **error\_ids** | Error taxonomy entries triggered, if any |
| **session\_id** | The session in which this evidence was produced |

Evidence records are immutable once written.
They are never updated — only appended.

## Write Authority

Only two components may write evidence to the Student Model:

- The **Assessment Engine** — after evaluating an exercise attempt
- The **Tutor Orchestrator** — for interaction-level signals not tied to a specific exercise

No other component may write. No student input may write directly.

This constraint protects the integrity of the evidence store.
A mastery computation is only as trustworthy as the evidence beneath it.

---

# Mastery Computation

Mastery at any canonical node is a **computed property**.

It is derived on demand from the evidence store, weighted by
graph structure and recency. It is never stored as a direct value.

## Computation Inputs

| Input | Source | Role |
|---|---|---|
| **Evidence records** | Student Model | Raw performance history per node |
| **Prerequisite edges** | Curriculum Graph | Structural context for mastery depth |
| **Mastery criteria** | Curriculum Graph | Definition of each mastery level per node |
| **Recency weights** | Student Model | How recently evidence was produced |
| **Error persistence** | Student Model | Whether misconceptions have been resolved |

## Computation Logic

Mastery at a node is computed as follows:

**1. Collect evidence** for the target node — all records against this node id, ordered by timestamp.

**2. Apply recency weighting** — more recent evidence carries more weight than older evidence. Evidence that has not been refreshed decays in influence over time, but never disappears.

**3. Assess prerequisite mastery** — a student cannot be at mastery level N on a node if prerequisite nodes are significantly below the level required to support N. The graph structure bounds the computation upward.

**4. Evaluate error persistence** — active unresolved errors identified in the error taxonomy reduce the computed mastery level. Resolved errors do not penalise but remain in the record.

**5. Apply mastery criteria** — the canonical mastery criteria for this node define what the evidence must demonstrate to reach each level. The computation returns the highest level the evidence supports.

## Mastery Decay

Because mastery is computed from recency-weighted evidence,
it naturally reflects the passage of time.

Evidence that is old and has not been reinforced carries less weight
in the computation. This means a student who has not engaged with a
node for an extended period will see a lower computed mastery level —
not as a punishment, but as an honest reflection of demonstrated
current ability.

Decay is gradual and proportional. It does not erase evidence.
It reduces its weight in the computation until new evidence is added.

---

# Error Taxonomy

The error taxonomy is a structured classification of misconceptions
and error patterns observed in student performance.

## Error Record

Each error entry in the Student Model captures:

| Field | Description |
|---|---|
| **id** | Unique error record identifier |
| **node\_id** | Canonical node where the error was observed |
| **error\_type** | Classification from the error taxonomy |
| **first\_observed** | Timestamp of first occurrence |
| **last\_observed** | Timestamp of most recent occurrence |
| **occurrence\_count** | How many times this error has appeared |
| **resolved** | Whether subsequent evidence shows the misconception is corrected |
| **resolution\_timestamp** | When resolution was confirmed, if applicable |

## Error Classification

Errors are classified by type across two dimensions:

**By origin:**

| Type | Description |
|---|---|
| **Conceptual** | Fundamental misunderstanding of the concept itself |
| **Procedural** | Correct understanding but incorrect execution of steps |
| **Interpretive** | Misreading or mismodelling the problem structure |
| **Transferral** | Applying a rule from one context incorrectly in another |

**By scope:**

| Scope | Description |
|---|---|
| **Node-local** | Error appears only within a specific node |
| **Cross-cutting** | Error pattern appears across multiple nodes, suggesting a deeper gap |

Cross-cutting errors are particularly significant. They indicate
a foundational misconception that the orchestrator must surface
and address before progression can be reliable.

---

# Confidence Layer

Mastery and confidence are tracked separately.

A student may demonstrate mastery level 4 on a node — solving
correctly and efficiently — but express low confidence in doing so.
Conversely, a student may express high confidence while producing
evidence that supports only level 2.

Confidence is a self-reported signal. Mastery is a computed property.
Neither overrides the other, but both inform the orchestrator's
response strategy.

| Signal | Source | Nature |
|---|---|---|
| **Mastery** | Computed from evidence | Objective, graph-grounded |
| **Confidence** | Student-reported or inferred from behaviour | Subjective, interaction-grounded |

The orchestrator uses the gap between mastery and confidence
to detect two important states:

- **Overconfidence** — high confidence, low mastery. Requires careful
  challenge without discouragement.
- **Underconfidence** — high mastery, low confidence. Requires
  affirmation and progressive exposure to confirm the student's
  own demonstrated ability.

Confidence signals are stored in the Student Model as
interaction-level observations, separate from evidence records.

---

# Session Reconstruction

At the start of each session, the orchestrator reconstructs
a minimal working context from the Student Model.

The reconstruction is **bounded and purposeful** — it extracts
only what is needed to be pedagogically coherent, not a replay
of prior sessions.

## Reconstruction Elements

| Element | Description | Source |
|---|---|---|
| **Active profile** | The curriculum profile currently in use | Student Model |
| **Current node** | The canonical node last under active study | Student Model |
| **Recent evidence summary** | Compressed summary of last N evidence records | Student Model |
| **Unresolved errors** | Active error taxonomy entries not yet resolved | Student Model |
| **Readiness snapshot** | Computed mastery state projected through active profile | Computed on demand |
| **Confidence state** | Most recent confidence signals per active node | Student Model |

## Reconstruction Constraints

- Reconstruction must not reproduce session history verbatim.
- The context must be minimal — sufficient for coherence, not exhaustive.
- Reconstruction is read-only. No evidence is written during reconstruction.
- The orchestrator uses the reconstructed context to orient the session, not to narrate it to the student.

---

# Readiness Projection

The Student Model exposes a readiness projection operation.

Given an active or candidate curriculum profile, the readiness
projection computes how prepared the student currently is for
that curriculum — expressed as a score per node and in aggregate.

## Projection Formula

For each required node in the profile:

```
node_readiness = min(computed_mastery, profile_target) / profile_target
weighted_readiness = node_readiness × node_weight
```

Aggregate readiness is the weighted sum across all required nodes,
normalised to a 0.0–1.0 scale.

A readiness score of 1.0 means all required nodes are at or above
their mastery targets, weighted by exam importance.

## Projection Uses

- **Gap delta** — comparing readiness under two profiles to identify transition gaps
- **Progress reporting** — showing the student how far they have come toward exam readiness
- **Orchestrator planning** — identifying the highest-leverage nodes to prioritise next
- **Profile comparison** — assessing how demanding a new curriculum would be given current state

---

# Domain Ownership

The Student Model belongs to the student.

Its evidence records, computed mastery states, error history,
confidence signals, and readiness projections are the student's
data. They are built through the student's own interaction
and effort, and they represent the student's intellectual journey.

## Ownership Implications

- The student may request a view of their own mastery state and readiness at any time.
- The student may not directly write to or modify the evidence store.
- Staff and system components may read the Student Model to serve the student.
- Staff and system components may not read the Student Model for purposes unrelated to tutoring the student without explicit consent.
- The implementation of the Student Model — its schema, computation logic, internal structure — is never exposed to the student.

The student sees their mastery, their progress, their readiness.
They do not see an evidence store, a computation formula, or a data model.

---

# Constraints Summary

- Mastery is computed from evidence, never assigned or stored directly.
- Evidence records are immutable. They accumulate and are never modified.
- Write authority belongs exclusively to the Assessment Engine and Tutor Orchestrator.
- Mastery computation is bounded upward by prerequisite mastery in the canonical graph.
- Mastery decay is natural and gradual — a function of recency weighting, not a punitive reset.
- Error taxonomy tracks both node-local and cross-cutting misconceptions.
- Cross-cutting errors must be surfaced and addressed before reliable progression can continue.
- Confidence and mastery are tracked separately. Neither overrides the other.
- Session reconstruction is minimal, bounded, and read-only.
- Readiness projection is computed on demand by crossing mastery state with a curriculum profile.
- The Student Model belongs to the student. Implementation details are never exposed to them.

---
