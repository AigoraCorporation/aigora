<div align="center">

<p align="center">
  <img src="assets/logo.png" alt="AIGORA" width="200"/>
</p>

<h3 align="center">AIGORA</h3>

<p align="center">

![Architecture Status](https://img.shields.io/badge/status-architecture%20design-blue)
![Language](https://img.shields.io/badge/learning%20language-Portuguese-green)
![Docs](https://img.shields.io/badge/docs-doc--first-orange)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

</p>

An AI-driven mathematics learning architecture designed to guide
students from foundational knowledge to competitive university-level performance.

Structured. Adaptive. Elite-focused.

**Current stage:** Architecture Design

Primary learning language: **Portuguese 🇧🇷**
Engineering documentation: **English**

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

# Core Concepts

AIGORA is built around three central architectural components:

| Component | Role |
|------|------|
| **Tutor Orchestrator** | Coordinates tutoring decisions and system behavior |
| **Student Model** | Stores evidence of student performance and computes mastery |
| **Curriculum Graph** | Represents mathematical knowledge and prerequisite structure |

Together, these components allow the system to guide learning progression
while maintaining transparency, consistency, and curriculum grounding.

---

# Target Audience

AIGORA is designed for Portuguese-speaking students,
particularly those preparing for Brazilian university entrance exams
such as **FUVEST**, **ENEM**, and other vestibular examinations.

---

# Language Policy

See the full language policy:

- [Language Policy](docs/conventions/language-policy.md)

---

# Documentation Map

The project documentation is organized as follows:

| Area | Description |
|-----|-------------|
| Vision | Strategic direction of the project |
| Architecture | System design and interaction model |
| Curriculum | Mathematical curriculum structure |
| Operations | Development workflow and Git processes |
| Conventions | Repository standards and guidelines |

Key documents:

- [Project Vision](docs/00-vision/vision.md)
- [Architecture Overview](docs/02-architecture/overview.md)
- [Development Workflow](docs/06-operations/workflow.md)

---

# Project Status

AIGORA is currently in the **architecture and system design phase**.

The current focus of the project is:

- defining the system architecture
- modeling the curriculum structure
- establishing repository governance
- preparing the foundation for future implementation

Implementation of system components will begin after the architectural
design stabilizes.

---

# Releases & Changelog

All notable changes to this project are documented in:

- [CHANGELOG.md](./CHANGELOG.md)

Latest release:

- v0.1.0 — Architecture Foundations

---

# Strategic Foundation

The conceptual basis of the project is defined in the following documents:

- [Project Vision](docs/00-vision/vision.md)
- [Goals & Non-Goals](docs/00-vision/goals-non-goals.md)

These documents define the long-term direction of the project and
establish clear boundaries for its scope.

---

# System Architecture

The system architecture defines how AI components, curriculum models,
and evaluation mechanisms interact.

- [System Overview](docs/02-architecture/overview.md)

- Engineering architecture docs:
  - [Interaction Model](docs/engineering/architecture/interaction-model.md)
  - [Tutor Orchestrator](docs/engineering/architecture/tutor-orchestrator.md)
  - [Curriculum Graph](docs/engineering/architecture/curriculum-graph.md)

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
- [Branch Naming Convention](docs/conventions/branch-naming.md)

Every change must:

1. originate from an Issue
2. be implemented in a dedicated branch
3. follow the commit convention
4. be submitted via Pull Request
5. pass CI checks

---

# Contributing

Contributions are welcome, but all work must follow the project's
engineering workflow.

Before contributing, please read:

- [Development Workflow](docs/06-operations/workflow.md)
- [Contributing Guide](CONTRIBUTING.md)

All changes must originate from a GitHub Issue.

---

# Repository Governance

To maintain consistency and quality, the repository enforces:

- [Commit Convention](docs/conventions/commits.md)
- [Branch Naming Convention](docs/conventions/branch-naming.md)
- [Pull Request Template](.github/pull_request_template.md)

The `main`, `release`, and `dev` branches are protected and cannot be updated directly.

---

# Roadmap & Tasks

Project work is tracked through GitHub Issues and the project board.

All development activities must originate from a documented Issue.

- [View Open Issues](https://github.com/AigoraCorporation/aigora/issues)
- [View Project Board](https://github.com/AigoraCorporation?tab=projects)

---

# Related Requirements

The architecture is guided by a set of system constraints that define
key technical, architectural, and product boundaries.

- [System Constraints](docs/01-requirements/constraints.md)

---

## Setup (Required)

After cloning the repository, run:

```bash
npm install
```

This installs the development dependencies used by the repository
tooling and CI checks.