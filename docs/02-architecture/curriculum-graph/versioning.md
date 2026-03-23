# Curriculum Graph Versioning

This document defines how changes to the canonical graph and curriculum
profiles are versioned, communicated, and managed over time.

The versioning scheme is designed to preserve the stability guarantees
that the graph provides to the Student Model and the orchestrator:
node ids are permanent, mastery state is portable, and profiles are
consistent views over a stable foundation.

---

## Core Constraint

> Node ids are the permanent identity of a concept.
> They must never change after a node is published.

All versioning decisions flow from this constraint.
Because mastery evidence in the Student Model is keyed by canonical
node id, changing an id would silently orphan student data.
Stability of ids is a data integrity requirement, not a convention.

---

## Versioning the Canonical Graph

### Version Format

The canonical graph uses **semantic versioning**: `MAJOR.MINOR.PATCH`.

```
<MAJOR>.<MINOR>.<PATCH>
```

| Component | Meaning |
|---|---|
| `MAJOR` | Breaking change — removes or renames a published node id |
| `MINOR` | Backward-compatible addition — new nodes or edges added |
| `PATCH` | Backward-compatible correction — clarifies existing content without changing ids or semantics |

### What Triggers Each Version Component

**PATCH** — no structural change, no semantic change to how
mastery is interpreted or measured:

- Correcting a typo in a `name` or `description`
- Clarifying a `mastery_criteria` entry without changing its meaning
- Adding an entry to `error_taxonomy` that does not affect existing entries
- Fixing a dangling reference that was an authoring error

**MINOR** — adds new content; existing content is unchanged:

- Adding a new canonical node
- Adding a new prerequisite edge between existing nodes
- Adding a new regression target to an existing node
- Adding a new top-level domain or subtopic category

**MAJOR** — breaks the stability contract:

- Removing a published canonical node (its id would become dangling)
- Renaming a node id (even if the old id is aliased)
- Changing a prerequisite edge type from soft to hard (or vice versa)
  in a way that alters orchestrator enforcement behaviour
- Redefining `mastery_criteria` such that a student's historical
  evidence would yield a different computed mastery level

### Deprecation Before Removal

Nodes may not be removed without a deprecation period.

The lifecycle of a node that must be removed:

1. **Deprecated** — the node is marked deprecated in the `MINOR` release.
   All profiles that reference it are notified. The node remains fully
   operational. New profiles should not reference it.

2. **Replaced** (optional) — a `replaced_by` field may point to the
   node id that supersedes it, if applicable.

3. **Removed** — the node is removed in the next `MAJOR` release.
   All profiles must drop the reference before the MAJOR lands.

A node may not be removed in the same release it is deprecated.

### Changelog

Every graph version increment must be accompanied by a changelog entry
that describes:

- The version number
- The date of publication
- A list of additions, changes, and deprecations
- For removals: the node id removed and the reason

The changelog lives at `docs/curriculum-rag/CHANGELOG.md`.

---

## Versioning Curriculum Profiles

### Profile Version Format

Profiles use a separate **semantic versioning** scheme, independent
of the canonical graph version:

```
<MAJOR>.<MINOR>.<PATCH>
```

A profile version tracks changes to the profile itself, not to the
canonical graph it references.

### What Triggers Each Profile Version Component

**PATCH**:

- Correcting a typo in a profile field
- Adjusting a node weight without changing which nodes are required
- Clarifying an `exam_skill_overlay` entry without changing its scope

**MINOR**:

- Adding a node to `required_nodes`
- Increasing a mastery target for a specific node
- Adding a new entry to `exam_skill_overlay`
- Adding a new recommended step in `progression_path`

**MAJOR**:

- Removing a node from `required_nodes`
- Decreasing a mastery target for a specific node (lowers expectations)
- Removing an `exam_skill_overlay` entry
- Changing the profile id (not permitted; a new profile must be created instead)

### Canonical Graph Version Pinning

Every profile declaration must specify the minimum canonical graph
version it was authored against:

```
requires_graph_version: "1.4.0"
```

This means: this profile is valid when used with canonical graph
version 1.4.0 or any backward-compatible version (i.e. any 1.x.y
where x ≥ 4, or any 2.0.0+ if migration has been verified).

When a MAJOR canonical graph version is released, all profiles must
be reviewed and their `requires_graph_version` updated before
they can be activated against the new graph version.

### Profile Retirement

Profiles are retired, not deleted, when a curriculum becomes obsolete.

A retired profile:

- Is no longer offered as an active curriculum option for new students
- Remains in the repository for historical reference and data consistency
- Has a `status: retired` field and a `retired_at` date

Students whose mastery state was accumulated under a retired profile
retain that state. Their canonical mastery is unaffected.

---

## Compatibility Matrix

The system must maintain an explicit compatibility matrix that
maps profile versions to the canonical graph versions they support.

| Profile | Profile Version | Min Graph Version | Max Graph Version | Status |
|---|---|---|---|---|
| `profile.fuvest` | 1.0.0 | 1.0.0 | 1.x.x | Active |
| `profile.enem` | 1.0.0 | 1.0.0 | 1.x.x | Active |

This matrix is updated whenever:

- A new canonical graph MAJOR version is published
- A profile's `requires_graph_version` is updated
- A profile is retired

---

## Summary of Versioning Principles

- Node ids are permanent. Stability of ids is a data integrity guarantee.
- Canonical graph and profiles are versioned independently.
- Both use semantic versioning: MAJOR for breaking changes, MINOR for additions, PATCH for corrections.
- Nodes cannot be removed without a deprecation period spanning at least one MINOR release.
- Profile ids are also permanent. A new exam edition results in a new profile, not a mutation.
- Every profile pins the minimum canonical graph version it requires.
- Retired profiles are preserved for historical consistency; they are never deleted.
