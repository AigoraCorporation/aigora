# Canonical CSV Model — Curriculum Graph

## Overview

This document defines the **canonical CSV data contract** for exporting the CurriculumGraph.

It specifies:
- all required CSV files
- their structure and purpose
- column definitions and types
- required vs optional fields
- ID conventions
- example rows

This document is **implementation-ready** and must be followed strictly by any CSV exporter.

---

## ID Conventions

All identifiers must follow consistent naming conventions:

| Entity | Format | Example |
|------|--------|--------|
| Node ID | dot-separated namespace | `math.algebra.linear-equations` |
| Profile ID | prefix + namespace | `profile.sat-math` |
| Edge Type | snake_case enum | `hard_prerequisite` |

### Rules

- IDs must be **globally unique**
- IDs must be **stable across versions**
- IDs must be **case-sensitive**
- No spaces allowed in IDs

---

## Data Types

| Type | Description |
|------|------------|
| string | UTF-8 text |
| float | decimal number |
| int | integer number |
| enum | predefined string values |
| list | represented via multiple rows |

---

# nodes.csv

## Purpose

Represents all knowledge nodes in the Curriculum Graph.

## Columns

| Column | Type | Required | Description |
|--------|------|----------|------------|
| id | string | yes | Unique node identifier |
| name | string | yes | Human-readable name |
| domain | string | yes | Domain/category |
| description | string | yes | Text description |

## Example

```csv
id,name,domain,description
math.arithmetic.fractions,Fractions,arithmetic,Understand fraction representation and operations.
```

---

# edges.csv

## Purpose

Represents relationships between nodes.

## Columns

| Column | Type | Required | Description |
|--------|------|----------|------------|
| type | enum | yes | Relationship type |
| source | string | yes | Source node ID |
| target | string | yes | Target node ID |

## Allowed Values

`type`:
- `hard_prerequisite`
- `soft_prerequisite` (future-safe)

## Example

```csv
type,source,target
hard_prerequisite,math.arithmetic.fractions,math.algebra.linear-equations
```

---

# profiles.csv

## Purpose

Represents learning profiles.

## Columns

| Column | Type | Required | Description |
|--------|------|----------|------------|
| id | string | yes | Unique profile ID |
| name | string | yes | Profile name |

## Example

```csv
id,name
profile.sat-math,SAT Math
```

---

# profile_mastery_targets.csv

## Purpose

Defines mastery level targets per node for each profile.

## Columns

| Column | Type | Required | Description |
|--------|------|----------|------------|
| profile_id | string | yes | Profile ID |
| node_id | string | yes | Node ID |
| mastery_level | int | yes | Target mastery level |

## Rules

- One row per (profile_id, node_id)
- Must reference valid node

## Example

```csv
profile_id,node_id,mastery_level
profile.sat-math,math.arithmetic.fractions,3
profile.sat-math,math.algebra.linear-equations,4
```

---

# profile_node_weights.csv

## Purpose

Defines importance weights for nodes within a profile.

## Columns

| Column | Type | Required | Description |
|--------|------|----------|------------|
| profile_id | string | yes | Profile ID |
| node_id | string | yes | Node ID |
| weight | float | yes | Relative importance |

## Rules

- weight > 0
- normalized or raw (exporter responsibility)

## Example

```csv
profile_id,node_id,weight
profile.sat-math,math.arithmetic.fractions,1.0
profile.sat-math,math.algebra.linear-equations,2.0
```

---

# profile_progression_paths.csv

## Purpose

Defines ordered learning sequence for each profile.

## Columns

| Column | Type | Required | Description |
|--------|------|----------|------------|
| profile_id | string | yes | Profile ID |
| position | int | yes | Order in sequence |
| node_id | string | yes | Node ID |

## Rules

- position must start at 0
- positions must be contiguous
- sequence must respect prerequisites

## Example

```csv
profile_id,position,node_id
profile.sat-math,0,math.arithmetic.fractions
profile.sat-math,1,math.algebra.linear-equations
```

---

# Consistency Rules

All CSV files must satisfy:

- Referential integrity:
  - node_id must exist in nodes.csv
  - profile_id must exist in profiles.csv

- No duplicated rows for same primary key

- Encoding must be UTF-8

---

# Primary Keys

| File | Primary Key |
|------|------------|
| nodes.csv | id |
| edges.csv | (type, source, target) |
| profiles.csv | id |
| profile_mastery_targets.csv | (profile_id, node_id) |
| profile_node_weights.csv | (profile_id, node_id) |
| profile_progression_paths.csv | (profile_id, position) |

---

# Non-Goals

This document does NOT define:

- CSV export implementation
- Neo4j import logic
- Cypher queries
- File storage strategy

---

# Summary

This document defines a **strict, implementation-ready CSV contract** for the Curriculum Graph.

It guarantees:
- consistency
- interoperability
- compatibility with future persistence layers
