# Curriculum Graph — Versioning Policy

The curriculum graph uses semantic versioning to communicate the nature
and impact of changes to canonical nodes and profiles.

---

## Graph Versioning

The graph version is declared in `metadata.yaml`:

```yaml
version: '1.0.0'
published_at: '2026-01-01'
```

Version increments follow these rules:

| Change type | Version bump |
|---|---|
| Adding a new canonical node | **MINOR** |
| Adding a new profile | **MINOR** |
| Correcting a description or mastery criteria text (non-breaking) | **PATCH** |
| Deprecating a node (setting `status: deprecated`) | **MINOR** |
| Removing a node from the canonical graph | **MAJOR** |
| Changing a node `id` | **MAJOR** (node ids are permanent — prefer deprecation) |
| Adding or changing a prerequisite edge | **MINOR** (may affect topological order) |
| Retiring a profile (`status: retired`) | **MINOR** |

---

## Node Lifecycle

1. **Active** — default state; the node is in full use.
2. **Deprecated** — the node is superseded by another; set `status: deprecated`,
   populate `deprecated_since` and optionally `replaced_by`. Deprecated nodes
   remain in the graph for backward compatibility.
3. **Removed** — only via a MAJOR version bump after a migration period.

---

## Profile Lifecycle

A new exam edition always produces a **new profile** with a new `id`.
Existing active profiles are never mutated; they may be retired
(`status: retired`, `retired_at` set) once no students are enrolled.

---

## Changelog

Every graph release must include a changelog entry describing:

- The version number and publication date
- A list of additions, changes, and deprecations
- For removals: the node id removed and the reason

The changelog is maintained in this repository's central changelog document.

---

## Profile Version Compatibility

Profiles declare the minimum graph version they require via
`requires_graph_version`. A profile is compatible with any graph version
that is backward-compatible with its declared minimum (i.e. same MAJOR,
equal or higher MINOR/PATCH).

The loader enforces this at load time and raises `GraphLoadError` for
incompatible combinations.
