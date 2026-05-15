# Curriculum Graph — Ports and Adapters

## Purpose

This document explains how the Curriculum Graph applies Ports and Adapters to isolate application logic from technical infrastructure.

---

## Concept

A port defines what the application needs.

An adapter defines how that need is fulfilled.

```text
Application Use Case
  ↓
Port
  ↑
Infrastructure Adapter
```

This allows infrastructure to change without changing application orchestration.

---

## Ports

Ports are contracts used by the application or domain layers.

They describe capabilities such as:

- loading data
- mapping payloads
- assembling graphs
- exporting graphs
- validating schemas
- persisting graphs

Ports should be expressed as protocols or interfaces.

---

## Adapters

Adapters are concrete implementations of ports.

In this project, adapters live under `infrastructure/`.

Examples:

| Port | Adapter |
|---|---|
| `CurriculumGraphRepository` | `Neo4jCurriculumGraphRepository` |
| `CurriculumGraphExporter` | `CsvCurriculumGraphExporter` |
| `CurriculumGraphExporter` | `JsonCurriculumGraphExporter` |
| `CurriculumGraphExporter` | `YamlCurriculumGraphExporter` |
| `CurriculumGraphParser` | `CurriculumGraphFileParser` |
| `CurriculumGraphSchemaValidator` | File schema validator implementation |

---

## Repository Port

`CurriculumGraphRepository` represents the persistence contract for the Curriculum Graph aggregate.

It belongs to the domain because it describes a domain-level persistence need.

It must not contain:

- Neo4j imports
- Cypher queries
- connection details
- transaction details

The Neo4j implementation belongs to infrastructure.

---

## Exporter Port

`CurriculumGraphExporter` defines the contract for exporting a graph.

Concrete exporters implement format-specific behavior:

- CSV
- JSON
- YAML

The use case does not know how each format is written. It only calls the exporter contract.

---

## File Processing Ports

The graph loading flow uses ports for file-oriented responsibilities:

- parser
- schema validator
- mapper
- assembler

These contracts allow the loading pipeline to remain independent from concrete file parsing and mapping implementations.

---

## Dependency Direction

The correct direction is:

```text
application/use_cases → application ports / domain contracts
infrastructure → application ports / domain contracts
```

The incorrect direction is:

```text
application/use_cases → infrastructure concrete classes
```

---

## Why This Matters

Ports and Adapters improve:

- testability
- infrastructure replacement
- dependency clarity
- API readiness
- long-term maintainability

They also make it possible to add new adapters without changing use case orchestration.

---

## Summary

The Curriculum Graph uses Ports and Adapters to keep the application core stable while allowing infrastructure to evolve independently.
