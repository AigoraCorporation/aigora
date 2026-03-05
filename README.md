<div align="center">

<p align="center">
  <img src="assets/logo.png" alt="AIGORA" width="200"/>
</p>

<h3>AIGORA</h3>

An intelligent mathematics learning system powered by AI,  
designed to guide students from foundational knowledge to competitive university-level performance.

Structured. Adaptive. Elite-focused.

</div>

---

# Project Overview

AIGORA is a **doc-first AI tutoring architecture** for mathematics education.

The system is designed to help students progress from basic concepts
to advanced problem solving by combining:

- structured curricula
- knowledge diagnostics
- adaptive learning strategies
- mastery tracking

Unlike generic AI chatbots, AIGORA is conceived as a **designed educational system**,
with explicit curriculum modeling and architectural governance.

---

# Strategic Foundation

The conceptual basis of the project is defined in the following documents:

- [Project Vision](docs/00-vision/vision.md)
- [Goals & Non-Goals](docs/00-vision/goals-non-goals.md)

These documents define the long-term direction of the project and
establish clear boundaries for its scope.

---

# Architecture System

The system architecture defines how AI components, curriculum models,
and evaluation mechanisms interact.

- [System Overview](docs/02-architecture/overview.md)

Architecture is designed **before implementation** to ensure scalability
and conceptual consistency.

---

# Curriculum Model

The curriculum is structured as a **prerequisite graph**, enabling
mastery-based progression through mathematical topics.

- [Scope Definition](docs/04-curriculum/scope-fuvest.md)
- [Topic Map](docs/04-curriculum/topic-map.md)

This structure allows the system to:

- identify knowledge gaps
- recommend learning paths
- reinforce conceptual understanding

---

# Development Workflow

All project work follows a strict engineering workflow.

- [Development Workflow](docs/06-operations/workflow.md)
- [Git Flow](docs/06-operations/git-flow.md)

Every change must:

1. originate from an Issue
2. be implemented in a dedicated branch
3. follow the commit convention
4. be submitted via Pull Request
5. pass CI checks

---

# Repository Governance

To maintain consistency and quality, the repository enforces:

- [Commit Convention](docs/conventions/commits.md)
- [Pull Request Template](.github/pull_request_template.md)
- [Contributing Guide](CONTRIBUTING.md)

The `main` branch is protected and cannot be updated directly.

---

## Roadmap & Tasks

Project work is tracked through GitHub Issues and the project board.

All development activities must originate from a documented Issue.

→ View Issues  
→ View Project Board

---

## Setup (Required)

After cloning the repository, run:

```bash
npm install
```

This installs the development dependencies used by the repository
tooling and CI checks.