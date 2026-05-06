# Release Roadmap

This document defines the planned evolution of AIGORA across versions.

It serves as the **single source of truth** for:
- upcoming releases
- current development focus
- component evolution

---

## Roadmap Overview

| Version | Name | Planned Date | Status | Primary Component | Details |
|--------|------|--------------|--------|------------------|--------|
| v0.1.0 | Architecture Foundations | 2026-03-06 | ✅ Released | Core | [Release](https://github.com/AigoraCorporation/aigora/releases/tag/v0.1.0) |
| v0.1.1 | Architecture v1 | 2026-03-27 | ✅ Released | Core | [Release](https://github.com/AigoraCorporation/aigora/releases/tag/v0.1.1) |
| v0.2.0 | Curriculum Graph (Core Runtime) | 2026-04-24 | ✅ Released | Curriculum Graph | [Release](https://github.com/AigoraCorporation/aigora/issues/71) |
| v0.2.1 | Curriculum Graph Persistence & Change Management | 2026-05-15 | 🚧 In Progress | Curriculum Graph | [Plan](https://github.com/AigoraCorporation/aigora/issues/124) |
| v0.3.0 | Orchestrator Core (Deterministic) | TBD | ⏳ Planned | Tutor Orchestrator | — |
| v0.4.0 | Student Model Foundation | TBD | ⏳ Planned | Student Model | — |

---

## Current Release

### v0.2.1 — Curriculum Graph Persistence & Change Management

**Status:** 🚧 In Progress  
**Primary Component:** Curriculum Graph  

#### Scope
- Persistence layer for Curriculum Graph
- Change management pipeline
- Data validation and consistency rules

#### Notes
This release focuses on stabilizing the Curriculum Graph as a reliable data foundation for future components.

---

## Upcoming Releases

### v0.3.0 — Orchestrator Core (Deterministic)

**Status:** ⏳ Planned  
**Primary Component:** Tutor Orchestrator  

#### Scope
- Core orchestration engine
- Deterministic decision rules
- Integration with Curriculum Graph

---

### v0.4.0 — Student Model Foundation

**Status:** ⏳ Planned  
**Primary Component:** Student Model  

#### Scope
- Student state representation
- Knowledge tracking
- Progress modeling

---

## Release Strategy

AIGORA follows a **component-driven release strategy**:

- Each release focuses on a primary component
- Cross-component integration happens incrementally
- Early versions prioritize architectural stability over feature completeness

---

## How to Update This Document

When a new release is created:

1. Move current release to "Released"
2. Update roadmap table
3. Promote next release to "Current"
4. Add a new future release if needed

---