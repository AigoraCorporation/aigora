# Responsibility Matrix

This document defines query ownership and architectural responsibilities between the Curriculum Graph and Tutor Orchestrator components inside AIGORA.

The objective is to establish clear bounded context ownership, reduce coupling, and prevent responsibility leakage across components.

---

# Core Responsibility Definition

```text
Curriculum Graph
=
Knowledge Topology Service

Tutor Orchestrator
=
Pedagogical Decision Engine
```

---

# Responsibility Matrix

| Query / Responsibility           | Owner              |
| -------------------------------- | ------------------ |
| Retrieve node prerequisites      | Curriculum Graph   |
| Retrieve node dependencies       | Curriculum Graph   |
| Resolve graph traversal          | Curriculum Graph   |
| Retrieve adjacent learning nodes | Curriculum Graph   |
| Execute Neo4j / Cypher queries   | Curriculum Graph   |
| Manage graph topology            | Curriculum Graph   |
| Manage curriculum versioning     | Curriculum Graph   |
| Evaluate progression eligibility | Tutor Orchestrator |
| Select next learning node        | Tutor Orchestrator |
| Apply pedagogical policies       | Tutor Orchestrator |
| Execute candidate ranking        | Tutor Orchestrator |
| Handle remediation logic         | Tutor Orchestrator |
| Handle regression logic          | Tutor Orchestrator |
| Evaluate mastery                 | Tutor Orchestrator |
| Execute deterministic sequencing | Tutor Orchestrator |

---

# Interaction Boundary

The Tutor Orchestrator should never query Neo4j directly.

All topology-related operations must be accessed through explicit Curriculum Graph contracts.

## Good

```text
Tutor Orchestrator asks the Curriculum Graph API
for adjacent learning nodes.
```

## Bad

```text
Tutor Orchestrator executes Cypher queries directly.
```

---

# Architectural Principle

The Curriculum Graph owns graph topology and dependency resolution.

The Tutor Orchestrator owns pedagogical orchestration and deterministic decision-making.
