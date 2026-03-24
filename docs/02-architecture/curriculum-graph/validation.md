# Curriculum Graph — Validation Rules

The curriculum graph is validated at three layers before any tutoring session
can use it:

1. **Structural (S1–S8)** — automated, enforced by CI; hard failures block merge.
2. **Semantic (SE1–SE8)** — semi-automated, surface as human review hooks; not
   CI-blocking but must be reviewed before merge.
3. **Operational (O1–O3)** — automated runtime safety checks enforced at load time.
   O4–O5 are planned for a future release.

---

## Structural Validators (S1–S8)

### S1 — ID Uniqueness

Every canonical node id must be unique within the graph. Duplicate ids are a
hard failure.

### S2 — ID Format

Node ids must match the pattern `<domain>.<subtopic>.<concept>`: three
dot-separated lowercase segments, hyphens allowed within segments, no
uppercase letters or special characters.

Profile ids must match `profile.<name>` where `<name>` is lowercase.

### S3 — Required Fields

Every canonical node must have:

- A non-empty `name`
- A non-empty `domain`
- A non-empty `description`
- All five mastery criteria levels non-empty
- At least **two** `error_taxonomy` entries

### S4 — Acyclicity

The prerequisite graph must be a directed acyclic graph (DAG). A cycle in
prerequisite edges is a hard failure.

### S5 — Referential Integrity

All `node_id` values referenced in `prerequisite_ids`, `regression_ids`, and
profile `required_nodes` must exist in the canonical graph.

### S6 — Progression Path Order

Within each profile's `progression_path`, a hard prerequisite of a node must
appear before that node in the list. Violations are a hard failure.

### S7 — Mastery Target Bounds

All `mastery_target` values in profile `required_nodes` must be in the range
`[1, 5]`. The value `0` (Unexposed) is not a valid curriculum target.

### S8 — Weight Non-Negativity

All `weight` values in profile `required_nodes` must be strictly positive
(`> 0`).

---

## Semantic Review Hooks (SE1–SE8)

Semantic hooks are not blocking — they surface as checklist items for human
reviewers. The following checks are currently **implemented**:

### SE2 — Description Exam Neutrality

Node descriptions must not reference any specific exam, institution, or
examination body. The validator flags descriptions containing keywords such
as "fuvest", "enem", "vestibular", "concurso".

### SE3 — Mastery Criteria Gradation

Mastery criteria levels 1–5 must describe a genuine progression of
competence. The validator flags nodes where two or more levels share
identical text.

### SE4 — Error Taxonomy Specificity

`error_taxonomy` entries must describe errors specific to the concept. The
validator flags entries whose descriptions contain generic phrases such as
"makes mistakes", "common error", or "can lead to errors".

### SE6 — Regression Path Relevance

Nodes without any `regression_ids` are flagged for human review to confirm
that regression targets are not needed given the node's `error_taxonomy`.

### SE7 — Profile Prerequisite Completeness

For each required node in a profile, all its hard prerequisites must also be
present in the profile's `required_nodes`. Omissions are flagged for reviewer
confirmation.

### SE8 — Exam Skill Overlay Containment

`exam_skill_overlay` entries must not describe mathematical concepts. The
validator flags entries whose descriptions contain mathematical keywords
(e.g. "equation", "fraction", "algebra").

### SE1, SE5 — Not Yet Implemented

SE1 (name uniqueness across concepts) and SE5 (mastery scale alignment)
require additional tooling and are planned for a future release.

---

## Operational Validators (O1–O3, implemented; O4–O5, planned)

Operational validators guard runtime safety. They run at graph load time
when `validate_graph(..., operational=True)` is called.

### O1 — Profile Coverage Completeness

Every node referenced in a profile's `required_nodes` must be reachable
from the graph root (i.e. have a valid prerequisite chain leading to a
foundational node).

### O2 — Topological Sort Feasibility

For every registered profile, the system must be able to produce a valid
topological ordering of its `required_nodes` respecting hard prerequisite
edges.

### O3 — Mastery Scale Alignment

The mastery scale used in `mastery_criteria` must be the canonical
0–5 scale defined in [curriculum-graph.md](../curriculum-graph.md).

---

### O4 — Profile Projection Completeness *(planned)*

For every registered profile, the system must be able to compute
a valid curriculum readiness score for any student state without
encountering missing node references or undefined mastery targets.

Profiles with nodes that lack mastery targets are operationally
incomplete and cannot be activated for a student session.

> **Status:** Not yet implemented. Will be enforced in a future release.

---

### O5 — No Profile Mutation of Canonical State *(planned)*

Any graph artifact that would, at runtime, cause the orchestrator
to write exam-specific data into a canonical node's fields is invalid.

Profiles must remain read-only lenses over the canonical graph. Any
runnable configuration that allows a profile to alter canonical
node content at runtime fails this validation.

> **Status:** Not yet implemented. Will be enforced in a future release.
