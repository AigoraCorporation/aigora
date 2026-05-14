# AIGORA Architecture

This documentation is organised into multiple architectural perspectives.

Each document explains the system from a different level of abstraction.

---

# Domain Architecture

| Document                             | Description                                         |
| ------------------------------------ | --------------------------------------------------- |
| [Architecture Overview](overview.md) | High-level system architecture and bounded contexts |

---

# Technical Architecture

| Document                                                               | Description                                                                 |
| ---------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| [Curriculum Graph — Technical Architecture](technical-architecture.md) | Technical architecture, dependency boundaries, and infrastructure isolation |
| [Architecture Decision Records (ADRs)](adr/README.md)                   | Architectural decisions, tradeoffs, and long-term design rationale          |

---

# Curriculum Graph Documentation

| Document                    | Description                                            |
| --------------------------- | ------------------------------------------------------ |
| [Overview](overview.md)     | Conceptual and domain architecture                     |
| [Domain Model](model.md)    | Canonical nodes, edges, and mastery structures         |
| [Schema](schema.md)         | Graph schema and validation rules                      |
| [Queries](queries.md)       | Query patterns and traversal semantics                 |
| [Validation](validation.md) | Structural, semantic, and operational validation rules |
| [Versioning](versioning.md) | Graph evolution and compatibility constraints          |

---

# Architectural Perspectives

The documentation intentionally separates:

| Perspective                 | Responsibility                                     |
| --------------------------- | -------------------------------------------------- |
| Domain Architecture         | Knowledge modeling and educational semantics       |
| Technical Architecture      | Dependency boundaries and implementation structure |
| Orchestration Architecture  | Tutoring flow and progression decisions            |
| Infrastructure Architecture | Persistence, APIs, and external integrations       |

This separation prevents coupling between educational semantics and implementation details.

---

# Architectural Decision Traceability

Significant architectural and technical decisions are documented through ADRs
(Architecture Decision Records).

ADRs preserve:

* architectural reasoning
* tradeoff analysis
* dependency decisions
* orchestration constraints
* infrastructure evolution decisions

This helps maintain long-term architectural consistency as the system evolves.
