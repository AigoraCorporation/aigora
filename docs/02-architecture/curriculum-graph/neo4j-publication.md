# Neo4j Publication Architecture — Curriculum Graph

## Objective

Define the official architecture for publishing the `CurriculumGraph` to CSV and Neo4j,
while preserving the existing file-based loading flow.

---

## Fundamental Principles

1. The `GraphLoader` remains the official entry point of the canonical graph
2. The graph is first built in memory, not directly in the database
3. Neo4j persistence is implemented via a port (`GraphRepository`) and an adapter
4. CSV is a derived artifact, not the primary source
5. Existing validations must be reused, not duplicated

---

## Complete Flow

```text
Canonical file (yaml/json)
    ↓
GraphLoader
    ↓
CurriculumGraph (in memory)
    ↓
GraphCsvExporter (optional)
    ↓
GraphRepository (port)
    ↓
Neo4jGraphRepository (adapter)
    ↓
Neo4j
    ↓
Post-persistence validations
````

---

## CSV Contract

The CSV structure used for graph publication is defined in:

- [`docs/05-data/canonical-csv-model.md`](../../05-data/canonical-csv-model.md)

This contract defines:

- all exported CSV files
- column structure and types
- required vs optional fields
- referential integrity rules

The `GraphCsvExporter` must strictly follow this contract.

--- 

## Components and Responsibilities

### GraphLoader (application)

Responsible for:

* reading the file
* validating schema
* building `CurriculumGraph`
* validating domain rules
* validating version

Does NOT:

* perform persistence
* export CSV
* communicate with the database

---

### GraphCsvExporter (application)

Responsible for:

* converting `CurriculumGraph` into CSV
* generating deterministic artifacts

---

### GraphRepository (application/port)

Persistence contract.

Defines:

* applying schema
* persisting graph
* validating persistence

---

### Neo4jGraphRepository (infrastructure)

Concrete implementation using Neo4j.

Responsible for:

* executing Cypher
* applying constraints
* persisting nodes and edges
* using UNWIND/MERGE in batches

---

### GraphPublicationService (application)

Flow orchestrator.

Responsible for:

1. loading the graph
2. optionally exporting CSV
3. applying schema
4. persisting data
5. validating persistence

---

## Validations

### Before persistence

* GraphSchemaValidator
* GraphValidator
* GraphVersionValidator

### After persistence

* node count validation
* consistency validation
* referential integrity validation

---

## Important Decisions

### ❗ GraphLoader MUST NOT be modified to interact with Neo4j

It remains file-based.

### ❗ Persistence must happen only through GraphRepository

Never directly in the service or loader.

### ❗ Cypher must not be scattered across the codebase

It must be centralized in the adapter or `.cypher` files.

---

## Anti-patterns (forbidden)

* GraphLoader using Neo4j
* Domain importing Neo4j driver
* Cypher inside CLI
* Domain logic inside infrastructure
* duplicated validations

---

## Conclusion

This architecture ensures:

* clear separation of concerns
* testability
* future evolution (other databases, APIs, etc.)
* control over AI-driven implementations in the project


