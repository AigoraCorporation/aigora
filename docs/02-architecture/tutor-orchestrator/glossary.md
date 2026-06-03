# Glossary

This document defines shared terminology used by the Tutor Orchestrator architecture documentation.

---

# Core Terms

| Term | Definition |
|---|---|
| Tutor Orchestrator | Component responsible for pedagogical orchestration and deterministic learning decisions. |
| Curriculum Graph | Component responsible for curriculum topology, prerequisites, dependencies, and traversal. |
| Learning Node | A curriculum unit that may be selected as a learning objective. |
| Candidate | A learning node prepared for orchestration evaluation. |
| Policy | A deterministic rule or constraint used to allow, block, or shape orchestration decisions. |
| Ranking | The process of ordering valid candidates according to deterministic preference rules. |
| Selection | The final orchestration commitment that chooses the next learning node. |
| Graph-Only | An orchestration strategy that depends only on curriculum topology. |
| Student-Aware | An orchestration strategy that depends on student learning state. |
| Hybrid | An orchestration strategy that combines curriculum topology and student learning state. |
| Deterministic Governance | The set of rules that ensures decisions are reproducible, auditable, and explainable. |
| Bounded Context | A clear ownership boundary that prevents responsibility leakage between components. |

---

# Engine Terms

| Term | Definition |
|---|---|
| Decision Engine | The deterministic reasoning core coordinating specialized orchestration engines. |
| Orchestration Engine | Coordinates orchestration flow and stage sequencing. |
| Policy Engine | Evaluates deterministic pedagogical constraints. |
| Strategy Engine | Scores and prioritizes orchestration candidates. |
| Selection Engine | Commits the final orchestration decision. |
| Auditability Engine | Preserves orchestration traceability and reproducibility. |
