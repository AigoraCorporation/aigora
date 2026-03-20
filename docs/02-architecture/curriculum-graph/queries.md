# Curriculum Graph — Query Model

## Overview

This document defines the query model of the AIGORA Curriculum Graph.

It describes the main query patterns used to navigate the graph,
retrieve canonical knowledge, apply curriculum overlays, and support
higher-level tutoring decisions.

The query model is designed to support:

- prerequisite reasoning
- curriculum-aware topic selection
- regression path identification
- profile-specific requirement lookup
- graph traversal for learning progression

This document builds on:

- [Curriculum Graph Overview](./index.md)
- [Curriculum Graph Domain Model](./model.md)
- [Curriculum Graph Schema](./schema.md)

---

## Query Design Principles

Queries against the Curriculum Graph must follow these principles:

- canonical knowledge must be queried independently of exam-specific overlays
- curriculum-specific requirements must be applied through profile traversal
- graph traversal must preserve prerequisite directionality
- query patterns must support explainable tutoring decisions
- student-specific state must be resolved outside the Curriculum Graph

---

## Query Categories

The Curriculum Graph supports five main query categories:

- **Canonical structure queries** — inspect topics and prerequisite relationships
- **Curriculum overlay queries** — retrieve profile-specific requirements
- **Traversal queries** — navigate prerequisite paths and progression chains
- **Regression queries** — identify fallback paths when mastery breaks down
- **Cross-profile queries** — compare or intersect curriculum requirements

---

## Canonical Structure Queries

### Get a topic by id

```cypher
MATCH (t:Topic {id: $topic_id})
RETURN t
```

### Get all topics in a domain

```cypher
MATCH (t:Topic {domain: $domain})
RETURN t
ORDER BY t.name
```

### Get direct prerequisites of a topic

```cypher
MATCH (p:Topic)-[r:PREREQUISITE_OF]->(t:Topic {id: $topic_id})
RETURN p, r
```

### Get direct dependent topics

```cypher
MATCH (t:Topic {id: $topic_id})-[r:PREREQUISITE_OF]->(d:Topic)
RETURN d, r
```

---

## Curriculum Overlay Queries

### Get all topics required by a profile

```cypher
MATCH (p:CurriculumProfile {id: $profile_id})-[r:REQUIRES]->(t:Topic)
RETURN t, r
ORDER BY r.progression_order
```

### Get mastery target for a topic in a profile

```cypher
MATCH (p:CurriculumProfile {id: $profile_id})-[r:REQUIRES]->(t:Topic {id: $topic_id})
RETURN t.id, t.name, r.mastery_target, r.weight, r.progression_order
```

### Get exam skills associated with a profile

```cypher
MATCH (p:CurriculumProfile {id: $profile_id})-[r:OVERLAYS_SKILL]->(s:ExamSkill)
RETURN s, r
ORDER BY r.priority
```

---

## Traversal Queries

### Get all prerequisite ancestors of a topic

```cypher
MATCH path = (p:Topic)-[:PREREQUISITE_OF*]->(t:Topic {id: $topic_id})
RETURN path
```

### Get all downstream topics unlocked by a topic

```cypher
MATCH path = (t:Topic {id: $topic_id})-[:PREREQUISITE_OF*]->(d:Topic)
RETURN path
```

### Get ordered prerequisite chain for a topic

```cypher
MATCH path = (p:Topic)-[:PREREQUISITE_OF*]->(t:Topic {id: $topic_id})
RETURN path
ORDER BY length(path)
```

### Get canonical topics required by a profile in progression order

```cypher
MATCH (p:CurriculumProfile {id: $profile_id})-[r:REQUIRES]->(t:Topic)
RETURN t, r
ORDER BY r.progression_order ASC
```

---

## Regression Queries

### Get regression targets for a topic

```cypher
MATCH (r:Topic)-[rel:REGRESSION_TARGET]->(t:Topic {id: $topic_id})
RETURN r, rel
```

### Get fallback topics combining regression targets and prerequisites

```cypher
MATCH (t:Topic {id: $topic_id})
OPTIONAL MATCH (r:Topic)-[:REGRESSION_TARGET]->(t)
OPTIONAL MATCH (p:Topic)-[:PREREQUISITE_OF]->(t)
RETURN r, p
```

---

## Cross-Profile Queries

### Get topics shared by two profiles

```cypher
MATCH (p1:CurriculumProfile {id: $profile_a})-[:REQUIRES]->(t:Topic)<-[:REQUIRES]-(p2:CurriculumProfile {id: $profile_b})
RETURN t
ORDER BY t.name
```

### Get topics required by one profile but not the other

```cypher
MATCH (p1:CurriculumProfile {id: $profile_a})-[:REQUIRES]->(t:Topic)
WHERE NOT EXISTS {
  MATCH (:CurriculumProfile {id: $profile_b})-[:REQUIRES]->(t)
}
RETURN t
ORDER BY t.name
```

### Compare mastery targets across profiles

```cypher
MATCH (p1:CurriculumProfile {id: $profile_a})-[r1:REQUIRES]->(t:Topic)<-[r2:REQUIRES]-(p2:CurriculumProfile {id: $profile_b})
RETURN
  t.name,
  r1.mastery_target AS profile_a_target,
  r2.mastery_target AS profile_b_target,
  r1.weight AS profile_a_weight,
  r2.weight AS profile_b_weight
ORDER BY t.name
```

---

## Orchestrator-Oriented Query Patterns

### Pattern 1 — Topic lookup

```cypher
MATCH (t:Topic {id: $topic_id})
RETURN t
```

### Pattern 2 — Prerequisite gap inspection

```cypher
MATCH (p:Topic)-[:PREREQUISITE_OF]->(t:Topic {id: $topic_id})
RETURN p
```

### Pattern 3 — Profile requirement projection

```cypher
MATCH (:CurriculumProfile {id: $profile_id})-[r:REQUIRES]->(t:Topic {id: $topic_id})
RETURN r.mastery_target, r.weight, r.progression_order
```

### Pattern 4 — Regression selection

```cypher
MATCH (r:Topic)-[:REGRESSION_TARGET]->(t:Topic {id: $topic_id})
RETURN r
```

### Pattern 5 — Next-topic progression lookup

```cypher
MATCH (p:CurriculumProfile {id: $profile_id})-[r:REQUIRES]->(t:Topic)
RETURN t, r
ORDER BY r.progression_order
```

---

## Query Boundaries

The Curriculum Graph query model does not solve student-specific state.

These responsibilities belong outside this component:

- checking current student mastery
- deciding whether mastery target has been met
- computing readiness scores
- tracking tutoring session history
- determining pedagogical strategy

---

## Performance Considerations

- use indexed ids for lookups
- limit traversal depth when necessary
- cache repeated orchestrator queries
- avoid duplicating nodes per profile

---

## Summary

The query model defines how the Curriculum Graph is navigated
to support tutoring decisions, progression, and curriculum adaptation.
