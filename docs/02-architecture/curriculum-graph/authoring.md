# Curriculum Graph — Authoring Guide

This document describes how to write canonical nodes and curriculum
profiles for the AIGORA Curriculum Graph.

All graph content lives under `src/curriculum_graph/data/graph/`
in the deployed package, and under `tests/fixtures/graph/` for tests.

---

## Directory Layout

```
graph/
    metadata.yaml
    nodes/
        <domain>/
            <subtopic>/
                <concept>.yaml
    profiles/
        profile.<name>.yaml
```

---

## System Roles

Each system component interacts with the graph in a specific, bounded way.
Understanding these roles prevents accidental coupling.

| Component | Role |
|---|---|
| **Curriculum Graph** | Owns canonical node definitions and prerequisite edges; defines mastery criteria and error taxonomy |
| **Tutor Orchestrator** | Reads the graph to make sequencing and regression decisions; never writes to it |
| **Assessment Engine** | Reads mastery criteria to generate and evaluate assessments; never modifies nodes |
| **Student Model** | Stores mastery state against node ids; never modifies graph structure |
| **Curriculum Profile** | Selects, weights, and sequences canonical nodes for a specific exam; never adds new nodes |

---

## Canonical Node Fields

Every canonical node YAML file must contain the following fields:

```yaml
id: <domain>.<subtopic>.<concept>   # permanent, lowercase, dot-separated
name: <Human-readable name>
domain: <domain>                    # matches first segment of id
description: >
  A concise, exam-neutral explanation of what the concept covers.
status: active                      # active | deprecated
mastery_criteria:
  '1': <Recognises — first exposure>
  '2': <Guided — can solve with support>
  '3': <Independent — solves without support>
  '4': <Efficient — fast and reliable>
  '5': <Transferable — applies to novel contexts>
error_taxonomy:
  - name: <Short error name>
    description: <Specific misconception, not a generic phrase>
  - name: <Second error>
    description: <Another specific misconception>
prerequisite_ids:
  - node_id: <domain>.<subtopic>.<concept>
    edge_type: hard   # hard | soft
regression_ids:
  - <node_id>        # node to revisit if student regresses on this concept
```

### Field Rules

- `id` — `domain.subtopic.concept`, all lowercase, hyphens allowed within
  segments, no uppercase. Permanent once published.
- `description` — must be exam-neutral. No exam names, dates, or scoring
  references.
- `mastery_criteria` — all five levels must be non-empty and genuinely
  distinct. Never reuse level text across two levels.
- `error_taxonomy` — at least two entries required. Each entry must name a
  specific, concept-scoped misconception; avoid generic phrases such as
  "makes mistakes" or "calculation error".
- `prerequisite_ids.edge_type` — use `hard` when the dependent concept
  cannot be meaningfully attempted without this prerequisite; use `soft`
  when the prerequisite significantly helps but is not strictly required.

---

## Curriculum Profile Fields

```yaml
id: profile.<name>                 # permanent; new edition = new profile
name: <Human-readable name>
version: '<semver>'
requires_graph_version: '<semver>'
status: active                     # active | retired
required_nodes:
  - node_id: <node_id>
    mastery_target: <1–5>         # 0 (Unexposed) is not a valid target
    weight: <positive float>
progression_path:
  - <node_id>                     # ordered; must respect hard prerequisite edges
exam_skill_overlay:
  - name: <Non-mathematical exam competency>
    description: <What this competency means in exam context>
```

### Profile Rules

- A new exam edition produces a **new profile** — never mutate an existing
  active profile.
- `required_nodes` must include all hard prerequisites of each listed node
  (SE7 review hook flags omissions for human review).
- `progression_path` must list prerequisite nodes before their dependents
  (S6 blocks merges that violate ordering).
- `exam_skill_overlay` is for non-mathematical competencies only (e.g.
  time management, strategic skipping). Mathematical concepts belong in
  canonical nodes, not overlays.

---

## Review Process

All changes to the canonical graph and all profiles must go through
the standard review process defined in
[pull-request-policy.md](../../06-operations/pull-request-policy.md).

New nodes and profiles undergo both automated validation (S1–S8, O1–O3)
and human semantic review (SE2–SE4, SE6–SE8) before merge.
