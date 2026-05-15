# Curriculum Graph — Graph Loading Pipeline

## Purpose

This document describes the pipeline used to load a `CurriculumGraph` from a file-based source.

The loading process is modeled as an explicit pipeline because it is a sequence of deterministic transformations and validations.

---

## Pipeline Overview

```text
file path
  ↓
parse payload
  ↓
validate schema
  ↓
map payload to domain objects
  ↓
assemble CurriculumGraph
  ↓
validate graph invariants
  ↓
validate graph version
  ↓
CurriculumGraph
```

---

## Main Components

### GraphLoadingPipeline

Coordinates the ordered execution of loading steps.

The pipeline receives a shared `GraphLoadingContext` and applies each step in sequence.

---

### GraphLoadingContext

Stores intermediate state during loading.

Typical fields include:

- source file path
- raw payload
- mapped nodes
- mapped edges
- mapped profiles
- graph version
- assembled graph

The context is intentionally internal to the loading flow.

---

### GraphLoadingStep

Defines the contract for each pipeline step.

Each step receives the shared context and mutates it with its output.

---

## Pipeline Steps

### Parse Step

Reads the file and produces a raw payload.

Input:

- file path

Output:

- raw payload

---

### Schema Validation Step

Validates the raw payload structure before mapping.

Input:

- raw payload

Output:

- validation success or failure

---

### Mapping Step

Maps the raw payload to domain-level objects.

Input:

- raw payload

Output:

- nodes
- edges
- profiles
- version

---

### Assembly Step

Assembles the mapped objects into a `CurriculumGraph` aggregate.

Input:

- nodes
- edges
- profiles
- version

Output:

- CurriculumGraph

---

### Graph Validation Step

Validates graph invariants.

Examples:

- no duplicate node ids
- no dangling references
- no invalid prerequisite relationships
- valid progression paths

---

### Version Validation Step

Validates graph version constraints.

Examples:

- version is present
- version has the expected format
- version is compatible with graph publication requirements

---

## Factory

The loading pipeline can be constructed by a factory responsible for wiring the default steps.

This keeps use cases focused on orchestration and keeps pipeline construction centralized.

```text
LoadGraphUseCase
  ↓
CurriculumGraphLoadingPipelineFactory
  ↓
GraphLoadingPipeline
```

---

## Why a Pipeline?

The pipeline pattern improves:

- readability
- testability
- step isolation
- extensibility
- failure diagnosis

A new loading step can be introduced without turning the use case into a large procedural method.

---

## Constraints

The loading pipeline must remain deterministic.

It must not:

- access Neo4j
- publish data
- call external APIs
- mutate student state

Persistence belongs to publication, not loading.
