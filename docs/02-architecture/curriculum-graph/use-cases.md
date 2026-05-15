# Curriculum Graph — Use Cases

## Purpose

This document describes the application use cases exposed by the Curriculum Graph bounded context.

Use cases are the official entry points into the application layer. External adapters should call use cases instead of directly accessing infrastructure components.

---

## Use Case Design

Each use case follows the same structure:

```text
Command → UseCase.execute(command) → Result
```

This pattern keeps application contracts explicit and avoids growing method signatures over time.

---

## LoadGraphUseCase

### Responsibility

Loads a `CurriculumGraph` from a file-based source.

### Input

`LoadGraphCommand`

Typical fields:

- file path

### Output

`LoadGraphResult`

Typical fields:

- loaded graph
- number of nodes loaded
- number of edges loaded
- number of profiles loaded
- graph version

### Flow

```text
file path
  ↓
GraphLoadingPipeline
  ↓
CurriculumGraph
  ↓
LoadGraphResult
```

The loading flow is implemented as an explicit pipeline. See [graph-loading-pipeline.md](graph-loading-pipeline.md).

### Notes

`LoadGraphUseCase` must remain file-based and deterministic. It must not access Neo4j or any persistence adapter directly.

---

## ExportGraphUseCase

### Responsibility

Exports a `CurriculumGraph` to a supported output format.

### Input

`ExportGraphCommand`

Typical fields:

- graph
- output directory
- output format

### Output

`ExportGraphResult`

Typical fields:

- output directory
- output format
- number of exported nodes
- number of exported edges
- success flag

### Flow

```text
ExportGraphCommand
  ↓
CurriculumGraphExporterRegistry
  ↓
CurriculumGraphExporter
  ↓
ExportGraphResult
```

### Supported Formats

- CSV
- JSON
- YAML

Export format resolution is implemented using the Strategy Pattern through a registry/factory. See [export-strategy.md](export-strategy.md).

---

## PublishGraphUseCase

### Responsibility

Publishes a loaded Curriculum Graph to a persistence backend.

### Input

`PublishGraphCommand`

Typical fields:

- graph source path
- publication options
- persistence validation options
- optional export options

### Output

`PublishGraphResult`

Typical fields:

- graph version
- number of nodes published
- number of edges published
- number of profiles published
- validation status

### Flow

```text
PublishGraphCommand
  ↓
LoadGraphUseCase
  ↓
CurriculumGraphRepository
  ↓
Neo4jCurriculumGraphRepository
  ↓
PublishGraphResult
```

### Notes

Publication orchestration belongs to the use case. There is no separate `GraphPublicationService` entry point anymore.

The use case depends on repository contracts and application ports, not concrete infrastructure details.

---

## QueryGraphUseCase

### Responsibility

Executes read operations against a Curriculum Graph.

### Input

`QueryGraphCommand`

Typical query types may include:

- get node by id
- get prerequisites
- get regression targets
- get progression information

### Output

`QueryGraphResult`

The result contains the query outcome in an application-level format.

### Flow

```text
QueryGraphCommand
  ↓
QueryGraphUseCase
  ↓
CurriculumGraph
  ↓
QueryGraphResult
```

---

## Use Case Boundary Rules

Use cases may:

- coordinate domain objects
- call ports
- orchestrate workflows
- return application results

Use cases must not:

- parse HTTP requests directly
- return HTTP response schemas
- execute Cypher directly
- write files directly without going through a port
- depend on concrete infrastructure implementations

---

## Summary

The use case layer defines what the Curriculum Graph application can do.

Current use cases:

| Use Case | Responsibility |
|---|---|
| `LoadGraphUseCase` | Load a graph from a file-based source |
| `ExportGraphUseCase` | Export a graph to CSV, JSON, or YAML |
| `PublishGraphUseCase` | Publish a graph to persistence |
| `QueryGraphUseCase` | Query a loaded graph |
