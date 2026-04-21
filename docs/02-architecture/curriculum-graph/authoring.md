# Curriculum Graph Authoring

This document defines the rules and conventions for authoring content
in the Curriculum Graph — canonical nodes, edges, and curriculum profiles.

It is the authoritative reference for anyone creating or modifying
graph artifacts. All contributions must comply with this specification.

---

## Authoring Authority

The canonical graph is a staff-curated artifact.
Students and the tutoring runtime do not author graph content.

| Actor | Authority |
|---|---|
| **Curriculum author** | Proposes and maintains canonical nodes, edges, and profiles |
| **Reviewer** | Validates proposals according to this specification |
| **Orchestrator** | Reads the graph; never writes to it |
| **Student Model** | Stores mastery state against node ids; never modifies graph structure |

All changes to the canonical graph and all profiles must go through
the standard review process defined in [pull-request-policy.md](../../05-engineering/governance/pull-request-policy.md).

---

## When to Create a New Node

A new canonical node is justified when all of the following are true:

1. **Distinct concept** — The concept cannot be expressed as a mastery level
   of an existing node. If a student could reach level 5 on an existing node
   and fully cover the new concept, a new node is not needed.

2. **Teachable in isolation** — The concept can be defined, described,
   and assessed independently of the context that motivated the addition.

3. **Standalone mastery criteria** — It is possible to define what mastery
   looks like at every level (0–5) for this concept specifically.

4. **At least one identifiable prerequisite** — Except for foundational
   primitives (e.g. Arithmetic), every node must have at least one
   prerequisite that already exists in the graph or is being added in the
   same contribution.

If any condition fails, the concept should be represented as a refinement
of an existing node, or as a profile-level skill overlay, not as a new node.

---

## When to Reuse an Existing Node

Reuse an existing node when:

- The new requirement is a depth variant of a concept already in the graph.
  Adjust the mastery target in the relevant profile instead.

- The distinction is exam-specific. If concept X is tested differently by
  Fuvest and ENEM, the node remains canonical and both profiles define
  their own mastery targets and skill overlays for it.

- The concept is a named sub-skill of an existing node. Prefer extending
  the node's `error_taxonomy` or `mastery_criteria` description rather
  than splitting the node.

- The concept has been removed from a profile but still exists in the
  canonical graph. Nodes are not deleted when a profile drops them;
  they remain available for future profiles.

---

## Node ID Convention

Node ids are permanent. Once a node is published, its id never changes.
Renaming the concept does not change the id.

### Format

```
<domain>.<subtopic>.<concept>
```

All segments are **lowercase**, **dot-separated**, and use **hyphens**
within a segment when the segment contains multiple words.

### Segments

| Segment | Description | Examples |
|---|---|---|
| `domain` | Top-level mathematical domain | `algebra`, `functions`, `geometry`, `combinatorics` |
| `subtopic` | Subdivision within the domain | `equations`, `graphing`, `polynomials` |
| `concept` | The specific concept being named | `linear-systems`, `vertex-form`, `prime-factorization` |

### Examples

| Concept | Node ID |
|---|---|
| Linear equations in one variable | `algebra.equations.linear-one-variable` |
| Vertex form of a quadratic | `functions.quadratic.vertex-form` |
| Domain and range of a function | `functions.general.domain-and-range` |
| Prime factorization | `algebra.arithmetic.prime-factorization` |
| Slope-intercept form | `functions.linear.slope-intercept` |

### Rules

- IDs are immutable after publication. Use versioning (see [versioning.md](versioning.md)) to manage changes.
- Abbreviations are not allowed. Use full descriptive words.
- The `concept` segment must be specific enough that two authors would
  arrive at the same id independently.
- If a concept spans two domains, assign it to the domain where it is
  primarily assessed. Cross-domain references are handled via `prerequisite_ids`.

---

## Profile ID Convention

Curriculum profile ids follow a simpler structure:

```
profile.<name>
```

Examples: `profile.fuvest`, `profile.enem`, `profile.enem-treineiro`.

Profile ids are also immutable. A new exam edition results in a new
versioned profile, not a mutation of an existing profile id.

---

## Node Authoring Checklist

When contributing a new node, every field must be populated:

| Field | Requirement |
|---|---|
| `id` | Follows the id convention; unique in the canonical graph |
| `name` | Human-readable, title-case concept name in English |
| `domain` | One of the defined top-level domains |
| `description` | Precise definition; does not mention any exam |
| `mastery_criteria` | Explicit description for each level 1–5 |
| `error_taxonomy` | At least two common misconceptions or error patterns |
| `prerequisite_ids` | All hard and soft prerequisites listed with edge type |
| `regression_ids` | At least one node to revisit if mastery breaks down |

A node with missing or placeholder fields will not pass review.

---

## Edge Authoring Rules

Edges encode prerequisite relationships between canonical nodes.
They are authored alongside the node that declares them in `prerequisite_ids`.

| Rule | Description |
|---|---|
| **No cycles** | The canonical graph is a DAG. Circular prerequisites are invalid. |
| **Hard prerequisites are strict** | Declare as hard only if the orchestrator should block progress entirely. |
| **Soft prerequisites are advisory** | Declare as soft if the concept is significantly easier with the prerequisite, but not impossible without it. |
| **Regression edges are recovery paths** | Declare regression targets that genuinely address the failure modes in `error_taxonomy`. |
| **No transitive redundancy** | If A → B → C already exists, do not also add A → C unless it is semantically meaningful to enforce it directly. |

---

## Profile Authoring Rules

A profile selects and weights canonical nodes. It does not define
new mathematical content.

| Rule | Description |
|---|---|
| **Only canonical nodes** | A profile may only reference node ids that exist in the canonical graph. |
| **No mastery criteria** | Profiles define mastery *targets*, not mastery *criteria*. Criteria live in the canonical node. |
| **Exam skill overlays are profile-only** | Skills like time pressure handling and strategic skipping belong in the profile's `exam_skill_overlay`. They are never added to canonical nodes. |
| **Weights are relative** | Node weights within a profile should reflect relative exam importance. They do not need to sum to any specific value. |
| **Progression path must be topologically consistent** | The recommended traversal order must respect the prerequisite edges of selected nodes. |
