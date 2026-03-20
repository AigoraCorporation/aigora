# Curriculum Graph — Schema

## Overview

This document defines the technical schema of the AIGORA Curriculum Graph
for implementation in Neo4j.

It specifies how the domain model is mapped into:

- node labels
- relationship types
- node properties
- relationship properties
- constraints
- indexes

This schema is derived from the conceptual definitions introduced in:

- [Curriculum Graph Overview](./index.md)
- [Curriculum Graph Domain Model](./model.md)

The schema is designed to preserve the architectural principles of AIGORA:

- mathematical knowledge must remain **exam-agnostic**
- curriculum requirements must remain **profile-specific**
- student-specific state must remain **outside** the Curriculum Graph

---

## Schema Design Principles

The Neo4j schema must satisfy the following principles:

- canonical mathematical knowledge is represented independently of any exam
- curriculum profiles are overlays over the canonical graph
- the graph must support directed prerequisite traversal
- the schema must remain extensible across multiple curricula
- student-specific mastery state must not be stored in the Curriculum Graph

---

## Node Labels

The Curriculum Graph is composed of the following primary node labels.

### `:Topic`

Represents a canonical mathematical concept.

### `:CurriculumProfile`

Represents an exam-specific curriculum profile.

### `:ExamSkill`

Represents an exam-specific skill overlay associated with a curriculum profile.

---

## Relationship Types

### `:PREREQUISITE_OF`
### `:REGRESSION_TARGET`
### `:REQUIRES`
### `:OVERLAYS_SKILL`

---

## Constraints

```cypher
CREATE CONSTRAINT topic_id_unique IF NOT EXISTS
FOR (t:Topic)
REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT curriculum_profile_id_unique IF NOT EXISTS
FOR (p:CurriculumProfile)
REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT exam_skill_id_unique IF NOT EXISTS
FOR (s:ExamSkill)
REQUIRE s.id IS UNIQUE;
```

---

## Indexes

```cypher
CREATE INDEX topic_name_index IF NOT EXISTS
FOR (t:Topic)
ON (t.name);

CREATE INDEX curriculum_profile_name_index IF NOT EXISTS
FOR (p:CurriculumProfile)
ON (p.name);

CREATE INDEX exam_skill_name_index IF NOT EXISTS
FOR (s:ExamSkill)
ON (s.name);
```

---

## Summary

This schema defines how the AIGORA Curriculum Graph is implemented in Neo4j,
preserving the separation between canonical knowledge and curriculum overlays.
