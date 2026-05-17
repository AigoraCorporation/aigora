# Traceability Model — ADRs, Issues, and Releases

## Purpose

This document defines the minimal governance model that ensures explicit,
verifiable traceability between architectural decisions (ADRs), implementation
(Issues), and delivery (Releases).

It does not introduce unnecessary rigidity. It establishes the minimum
constraint system needed to prevent invisible design drift.

---

## Entities

| Entity | Description |
|--------|-------------|
| **ADR** | An Architectural Decision Record documenting a binding technical decision |
| **ADR Milestone** | A deliverable checkpoint within an ADR that maps to implementation |
| **Issue** | A GitHub Issue representing a unit of implementation work |
| **Release** | A versioned delivery grouping ADR Milestones and their Issues |

---

## Relationships

```
ADR ──depends on──▶ ADR
ADR ──defines──▶ ADR Milestone
Issue ──references──▶ ADR Milestone
Issue ──depends on──▶ Issue (optional)
Release ──includes──▶ ADR Milestone
```

- An ADR may depend on one or more other ADRs.
- An ADR must define at least one milestone.
- A feature-level Issue must reference exactly one ADR Milestone.
- A Release must reference only ADR Milestones (not raw Issues).
- ADR dependencies must form a Directed Acyclic Graph (DAG).

---

## Invariants

1. **Every ADR must define at least one milestone.**
2. **Every feature-level Issue must reference exactly one ADR Milestone.**
3. **A Release must reference only ADR Milestones.**
4. **ADR dependencies must form a DAG** (no cycles).
5. **Each ADR Milestone included in a Release must have at least one Issue referencing it.**

---

## Exceptions

| Exception | Condition |
|-----------|-----------|
| Bugfix Issues may omit ADR linkage | The fix does not introduce architectural change |
| Chore Issues may omit ADR linkage | Maintenance tasks with no domain impact |
| Multi-ADR Issues must be explicitly justified | Documented in the Issue body |

---

## Enforcement

| Mechanism | What it enforces |
|-----------|-----------------|
| PR checklist | ADR linkage for feature Issues |
| CI — missing ADR references | Feature Issues must declare an ADR Milestone |
| CI — cyclic ADR dependencies | ADR DAG must remain acyclic |
| Release document | Must explicitly declare all ADR Milestones included |

---

## Required Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| ADR documents | `docs/02-architecture/[component]/adr/` | Record binding decisions and milestones |
| Release documents | `docs/releases/` | Declare ADR Milestones and Issues per release |
| Issue ADR fields | GitHub Issue body | Link Issue to ADR Milestone |

---

## DAG Topology

The traceability model defines three interconnected DAGs:

### 1. ADR DAG
```
ADR-001 ◀── ADR-002 ◀── ADR-003
```
Each ADR may depend on prior ADRs. Dependencies must not form cycles.

### 2. Issue DAG
```
Issue A ◀── Issue B ◀── Issue C
```
Each Issue may depend on prior Issues. The Issue DAG is scoped per Release.

### 3. Milestone-to-Issue Mapping
```
ADR Milestone ──▶ Issue (1..N)
```
Each milestone included in a Release must be referenced by at least one Issue.

---

## ADR Milestone Structure

Each ADR document must include a `## Milestones` section:

```markdown
## Milestones

| ID | Description | Status | Owner |
|----|-------------|--------|-------|
| M1 | Initial implementation | Done | @owner |
| M2 | Integration test coverage | Pending | @owner |
```

Issues reference milestones via the `ADR Milestone` field in their body.

---

## Release Document Structure

Each release must declare:

```markdown
## ADR Milestones Included
- ADR-001 / M1
- ADR-002 / M1

## Issues Included
- #126, #134, #137, ...
```

---

## Completeness Rule

A Release is only considered complete when:
- Every declared ADR Milestone has at least one Issue referencing it.
- Every included Issue is closed.
- The ADR DAG for included ADRs is acyclic.

---

## Related Documents

- [Engineering Policies](engineering-policies.md)
- [Pull Request Policy](pull-request-policy.md)
- `docs/02-architecture/[component]/adr/` — ADR documents
- `docs/releases/` — Release documents
