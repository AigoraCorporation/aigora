# System Constraints

This document defines architectural and product constraints
that must be respected across the AIGORA system design.

---

## Technical Constraints

- The system must follow a modular architecture.
- Components should remain loosely coupled.
- External LLM providers must be abstracted.

---

## Architectural Constraints

- The Tutor Orchestrator must coordinate tutoring decisions.
- The Student Model must represent learner state only.
- The Curriculum Graph must represent concept dependencies.
- Assessment logic must remain isolated in the Assessment Engine.

---

## Product Constraints

- Learning progression must be curriculum-driven.
- Tutoring interactions should remain interpretable.

---

## AI Integration Constraints

- LLM usage must be mediated through the LLM Interface.
- Responses should be grounded using retrieved learning material.