# Tutor Orchestrator Architecture

This documentation describes the architectural foundations, decision systems, orchestration model, and runtime integration strategy of the AIGORA Tutor Orchestrator.

---

# Recommended Reading Order

| # | Document | Why read it first |
|---|---|---|
| 1 | [Tutor Orchestrator](tutor-orchestrator.md) | Understand the core component and its responsibility. |
| 2 | [Interaction Model](interaction-model.md) | Understand how the orchestrator interacts with students and components. |
| 3 | [Architectural Responsibility Boundaries](architectural-responsibility-boundaries.md) | Understand ownership boundaries between orchestration and topology. |
| 4 | [Responsibility Matrix](responsibility-matrix.md) | Understand who owns each responsibility. |
| 5 | [Deterministic Orchestration Architecture](deterministic-orchestration-architecture.md) | Understand the global orchestration pipeline. |
| 6 | [Decision Engine Architecture](decision-engine-architecture.md) | Understand the engine-based internal decision architecture. |
| 7 | [Candidate Generation Model](candidate-generation-model.md) | Understand how learning nodes become candidates. |
| 8 | [Deterministic Orchestration Rule Model](deterministic-orchestration-rule-model.md) | Understand rule categories and policy evolution. |
| 9 | [Candidate Ranking Architecture](candidate-ranking-architecture.md) | Understand candidate prioritization. |
| 10 | [Learning Node Selection Strategy](learning-node-selection-strategy.md) | Understand final node selection. |
| 11 | [Curriculum Graph Contracts](curriculum-graph-contracts.md) | Understand service contracts with Curriculum Graph. |
| 12 | [Auditability and Decision Traceability](auditability-and-decision-traceability.md) | Understand decision reconstruction and auditability. |

---

# Foundations

| Document | Description |
|---|---|
| [Tutor Orchestrator](tutor-orchestrator.md) | Core orchestration responsibilities and pedagogical coordination model. |
| [Interaction Model](interaction-model.md) | Interaction dynamics, component coordination, and domain ownership. |
| [Architectural Responsibility Boundaries](architectural-responsibility-boundaries.md) | Service and component ownership boundaries. |
| [Responsibility Matrix](responsibility-matrix.md) | Cross-component responsibility mapping. |
| [Glossary](glossary.md) | Shared terminology used across Tutor Orchestrator documentation. |

---

# Orchestration

| Document | Description |
|---|---|
| [Deterministic Orchestration Architecture](deterministic-orchestration-architecture.md) | Global deterministic orchestration lifecycle and coordination. |
| [Event-Driven Pedagogical Flow](event-driven-pedagogical-flow.md) | Event-driven orchestration lifecycle. |
| [Orchestration Roadmap](orchestration-roadmap.md) | Future evolution of deterministic, student-aware, hybrid, and adaptive orchestration. |

---

# Decision Systems

| Document | Description |
|---|---|
| [Decision Engine Architecture](decision-engine-architecture.md) | Engine-based decision architecture and internal coordination. |
| [Candidate Generation Model](candidate-generation-model.md) | Candidate generation lifecycle. |
| [Deterministic Orchestration Rule Model](deterministic-orchestration-rule-model.md) | Rule categories and deterministic policy evolution. |
| [Candidate Ranking Architecture](candidate-ranking-architecture.md) | Deterministic ranking model. |
| [Learning Node Selection Strategy](learning-node-selection-strategy.md) | Learning progression selection behavior. |
| [Deterministic Orchestration Approaches](deterministic-orchestration-approaches.md) | Architectural orchestration alternatives. |

---

# Integration

| Document | Description |
|---|---|
| [Curriculum Graph Contracts](curriculum-graph-contracts.md) | gRPC integration contracts and boundaries. |
| [Tutor Orchestrator Container Diagram](tutor-orchestrator-container-diagram.md) | Runtime container architecture. |

---

# Governance and Observability

| Document | Description |
|---|---|
| [Deterministic Governance](deterministic-governance.md) | Shared deterministic guarantees and reproducibility rules. |
| [Auditability and Decision Traceability](auditability-and-decision-traceability.md) | Decision reconstruction and auditability. |

---

# Architectural Perspectives

The Tutor Orchestrator architecture intentionally separates:

| Perspective | Responsibility |
|---|---|
| Pedagogical Orchestration | Learning progression and orchestration decisions. |
| Decision Systems | Candidate generation, ranking, selection, and deterministic rules. |
| Integration Architecture | External systems and gRPC contracts. |
| Governance Architecture | Auditability, traceability, and deterministic guarantees. |
| Runtime Architecture | Containers, infrastructure, and deployment topology. |

This separation prevents orchestration logic, infrastructure concerns, and pedagogical rules from becoming tightly coupled.
