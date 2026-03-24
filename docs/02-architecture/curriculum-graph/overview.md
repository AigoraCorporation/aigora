# Curriculum Graph — Sub-package Overview

This directory contains the detailed design documents for the AIGORA
Curriculum Graph sub-package (`src/curriculum_graph`).

For the system-level picture, see the
[Architecture Overview](../overview.md) and
[Tutor Orchestrator](../tutor-orchestrator.md).

---

## Document Map

| Document | Purpose |
|---|---|
| [overview.md](overview.md) | This file — directory index and design context |
| [authoring.md](authoring.md) | How to write and submit canonical nodes and profiles |
| [validation.md](validation.md) | Structural, semantic, and operational validation rules (S1–S8, SE1–SE8, O1–O5) |
| [versioning.md](versioning.md) | Graph versioning policy and changelog convention |

---

## Package Structure

```
src/curriculum_graph/
    domain/
        enums.py          # MasteryLevel, EdgeType, NodeStatus, ProfileStatus
        models.py         # CanonicalNode, CurriculumProfile, CanonicalGraph, …
    application/
        repository.py     # CurriculumGraphRepository (abstract)
        queries.py        # CurriculumGraphQueryService
        validators.py     # StructuralValidator, SemanticValidator, OperationalValidator
    infrastructure/
        loaders/
            yaml_loader.py        # YAMLGraphLoader
        repositories/
            file_repository.py    # FileBasedCurriculumGraphRepository
    tests/
        fixtures/graph/   # YAML test graph (3 nodes, 1 profile)
        unit/             # Model, validator, query unit tests
        integration/      # File-based repository integration tests
```

---

## Design Principles

1. **Canonical graph is exam-agnostic.** No exam names, dates, or scores
   appear in canonical node fields.

2. **Profiles are read-only lenses.** A profile selects, weights, and
   sequences canonical nodes. It never modifies them.

3. **IDs are permanent.** Once a canonical node is published its `id`
   never changes, even if the node is renamed or deprecated.

4. **Validation is layered.** Structural rules are enforced by CI (hard
   failures). Semantic rules surface as human review hooks. Operational
   rules guard runtime safety.
