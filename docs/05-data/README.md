# Data Documentation

This directory contains **data contracts and data-related specifications** for AIGORA.

These documents define how data is structured, exchanged, and validated across the system.

---

## Contents

| Document | Description |
|----------|------------|
| [Canonical CSV Model](canonical-csv-model.md) | Defines the official CSV contract for exporting Curriculum Graph data |

---

## Scope

This directory includes:

- data formats (CSV, JSON, etc.)
- data contracts
- data validation rules
- data exchange specifications

---

## Non-Scope

This directory does NOT include:

- implementation details
- database-specific logic (e.g., Neo4j queries)
- application code

---

## Purpose

The goal of this directory is to ensure:

- consistency in data representation
- interoperability between system components
- clarity for future implementations (exporters, ingestion pipelines, etc.)

---

## Related Documents

- `docs/02-architecture/overview.md`
- `docs/02-architecture/curriculum-graph/neo4j-publication.md`
- `docs/01-requirements/constraints.md`

---

## Notes

All documents in this directory are considered **contracts**.

They must be:
- explicit
- unambiguous
- implementation-ready