# Curriculum Graph Validation

This document defines the validation rules applied to curriculum graph
artifacts — canonical nodes, prerequisite edges, and curriculum profiles.

Validations are grouped into three layers: structural, semantic, and
operational. Each layer addresses a distinct class of integrity concern.

---

## Validation Layers

| Layer | Concern | Applied at |
|---|---|---|
| **Structural** | Graph integrity and schema conformance | Authoring time and CI |
| **Semantic** | Conceptual soundness and pedagogical coherence | Review process |
| **Operational** | Runtime compatibility with the orchestrator and student model | Integration and deployment |

All three layers must pass before any artifact is merged into the canonical graph.

---

## Structural Validations

Structural validations verify that graph artifacts are well-formed
and internally consistent at the data level. They are automatable
and enforced by CI.

### S1 — ID Uniqueness

Every node id must be unique within the canonical graph.
Every profile id must be unique within the profile registry.

Duplication of any id is a hard failure.

### S2 — ID Format Conformance

All node ids must conform to the format defined in [authoring.md](authoring.md):

```
<domain>.<subtopic>.<concept>
```

Lowercase, dot-separated, hyphens within segments. No spaces, no
uppercase characters, no underscores.

The identifier format defines the canonical structure of ids; uniqueness
is enforced separately at the graph level (see S1).

Profile ids must conform to `profile.<name>`.

### S3 — Required Fields Present

Every canonical node must have all required fields populated:
`id`, `name`, `domain`, `description`, `mastery_criteria`,
`error_taxonomy`, `prerequisite_ids`, `regression_ids`.

Fields may not be empty strings or placeholder values.

### S4 — Acyclicity (DAG Invariant)

The canonical graph must be a directed acyclic graph (DAG).

A graph traversal must confirm that no cycle exists among
prerequisite edges. A cycle means two or more nodes form a
mutual prerequisite dependency, which is logically incoherent.

Cycle detection is a hard failure and blocks merge.

### S5 — Referential Integrity

All ids referenced in `prerequisite_ids` and `regression_ids`
of any node must resolve to an existing node in the canonical graph.

All node ids referenced in a profile's `required_nodes` and
`progression_path` must resolve to existing canonical nodes.

Dangling references are a hard failure.

### S6 — Progression Path Topological Order

The `progression_path` defined in a profile must respect the
prerequisite edges of the nodes it includes.

If node B has node A as a hard prerequisite, A must appear before B
in the profile's recommended traversal order.

### S7 — Mastery Target Bounds

All mastery targets defined in a profile must be in the range [1, 5].
A target of 0 (Unexposed) is meaningless as a curriculum target and
is invalid.

### S8 — Weight Non-Negativity

All node weights in a profile must be strictly positive numbers.
Zero or negative weights are not permitted.

---

## Semantic Validations

Semantic validations verify that the graph accurately and coherently
represents mathematical knowledge. They require expert judgement and
are enforced through the human review process.

### SE1 — Concept Distinctness

Each node must represent a concept that is meaningfully distinct
from all existing nodes.

Reviewers must verify that the proposed node cannot be expressed
as a higher mastery level of an existing node, and that splitting
an existing node into two is genuinely necessary.

### SE2 — Description Exam-Neutrality

Node descriptions must contain no reference to any specific exam,
institution, or curriculum context.

A description that mentions Fuvest, ENEM, or any exam-specific
framing must be revised before merge.

### SE3 — Mastery Criteria Gradation

The mastery criteria for levels 1–5 must describe a genuine
progression of competence for the specific concept.

Level 2 must be harder than level 1. Level 5 must be substantially
more demanding than level 3. Criteria that are ambiguous or
indistinguishable between adjacent levels fail this check.

### SE4 — Error Taxonomy Specificity

Entries in `error_taxonomy` must describe errors specific to the
concept being defined. Generic descriptions like "student may make
calculation errors" do not constitute a valid error taxonomy entry.

Each entry should name the misconception or error pattern precisely
and explain the reasoning failure it represents.

### SE5 — Prerequisite Soundness

Each declared hard prerequisite must represent a genuine cognitive
dependency: the concept being defined is not meaningfully approachable
without the prerequisite.

Reviewers must challenge prerequisites that appear habitual or
conventional rather than logically necessary.

Soft prerequisites must represent a genuine advantage in understanding,
not merely a topical adjacency.

### SE6 — Regression Path Relevance

Each `regression_id` must point to a node that addresses a root cause
identified in `error_taxonomy`.

Regression targets that are merely related topics — but not diagnostic
of the failure modes listed — do not satisfy this check.

### SE7 — Profile Completeness

A profile must include all canonical nodes that are prerequisites of
any node it lists as required. A profile cannot require depth in
quadratic functions while omitting linear functions if linear functions
is a hard prerequisite.

Reviewers must verify that the profile's `required_nodes` set is
closed under prerequisite dependencies at the declared mastery targets.

### SE8 — Exam Skill Overlay Containment

Skills listed in a profile's `exam_skill_overlay` must describe
non-mathematical competencies (e.g. time management, pattern selection,
error checking). Any skill that is a mathematical concept must be
moved to the canonical graph as a node, not placed in an overlay.

---

## Operational Validations

Operational validations verify that graph artifacts are compatible
with the runtime behaviour of the Tutor Orchestrator and the
Student Model. They are verified during integration testing.

### O1 — Orchestrator Traversability

The orchestrator must be able to resolve any required node in any
registered profile by traversing the canonical graph from its
foundational primitives.

A profile node that is unreachable — due to a gap in the prerequisite
chain — is an operational failure.

### O2 — Student Model Compatibility

All canonical node ids must be valid as evidence keys in the
Student Model's evidence store. Node ids that contain characters
incompatible with the evidence store's key format are invalid.

### O3 — Mastery Scale Alignment

The mastery scale used in `mastery_criteria` must be the canonical
0–5 scale defined in [overview.md](./overview.md).
Any node that implicitly assumes a different scale breaks mastery
computation in the Student Model.

### O4 — Profile Projection Completeness

For every registered profile, the system must be able to compute
a valid curriculum readiness score for any student state without
encountering missing node references or undefined mastery targets.

Profiles with nodes that lack mastery targets are operationally
incomplete and cannot be activated for a student session.

### O5 — No Profile Mutation of Canonical State

Any graph artifact that would, at runtime, cause the orchestrator
to write exam-specific data into a canonical node's fields is invalid.

Profiles must remain read-only lenses over the canonical graph. Any
runnable configuration that allows a profile to alter canonical
node content at runtime fails this validation.

---

## Validation Summary

| ID | Layer | Automatable | Hard Failure |
|---|---|---|---|
| S1 | Structural | Yes | Yes |
| S2 | Structural | Yes | Yes |
| S3 | Structural | Yes | Yes |
| S4 | Structural | Yes | Yes |
| S5 | Structural | Yes | Yes |
| S6 | Structural | Yes | Yes |
| S7 | Structural | Yes | Yes |
| S8 | Structural | Yes | Yes |
| SE1 | Semantic | No | Yes (review gate) |
| SE2 | Semantic | Partial (keyword scan) | Yes |
| SE3 | Semantic | No | Yes (review gate) |
| SE4 | Semantic | No | Yes (review gate) |
| SE5 | Semantic | No | Yes (review gate) |
| SE6 | Semantic | No | Yes (review gate) |
| SE7 | Semantic | Partial | Yes (review gate) |
| SE8 | Semantic | Partial (keyword scan) | Yes |
| O1 | Operational | Yes | Yes |
| O2 | Operational | Yes | Yes |
| O3 | Operational | Partial | Yes |
| O4 | Operational | Yes | Yes |
| O5 | Operational | Yes | Yes |
