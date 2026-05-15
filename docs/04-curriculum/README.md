# Curriculum Documentation

This directory defines the **pedagogical structure and learning pathways** used in AIGORA.

It represents how knowledge is organized, sequenced, and evaluated within the system.

---

## Overview

The curriculum is designed as a **structured, mastery-based learning graph**, where:

- topics are interconnected through prerequisite relationships
- progression depends on demonstrated mastery
- learning is guided by both structure and adaptation

---

## Contents

| Document | Description |
|----------|------------|
| [Curriculum Scope — Fuvest-Oriented Pathway](scope-fuvest.md) | Defines the scope, philosophy, and boundaries of the curriculum |
| [Topic Map](topic-map.md) | Defines the structured progression of topics and prerequisite graph |

---

## How to Read This Section

Start with:

1. **Scope Document**  
   → Understand *what is included* and *why*

2. **Topic Map**  
   → Understand *how topics are structured and connected*

---

## Conceptual Model

The curriculum is built on three core principles:

### 1. Mastery-Based Learning
Progression is based on demonstrated understanding, not completion.

### 2. Prerequisite Graph
Topics are connected through strict dependency relationships.

### 3. Adaptive Reinforcement
The system dynamically revisits prior topics when needed.

---

## Relationship with Other Areas

| Area | Description | Location |
|------|------|--------|
| Architecture | Defines how the curriculum is represented in the system | [`docs/02-architecture`](../02-architecture/overview.md) |
| Data | Defines how curriculum data is exported and exchanged | [`docs/05-data`](../05-data/README.md) |
| Engineering | Defines how the system is built and maintained | [`docs/06-engineering`](../06-engineering/README.md) |

---

## Scope Notes

- This is not a full national curriculum
- Focus is on **high-impact mathematical concepts**
- Designed initially for **Fuvest-level preparation**

---

## Future Evolution

This directory will expand to include:

- additional domains (trigonometry, probability, calculus)
- deeper topic decomposition
- learning objectives per node
- error taxonomy integration

---

## Summary

This directory defines **what the student learns and how learning is structured**.

It is the foundation for:

- Curriculum Graph (domain model)
- Tutor Orchestrator (learning strategy)
- Assessment Engine (evaluation)