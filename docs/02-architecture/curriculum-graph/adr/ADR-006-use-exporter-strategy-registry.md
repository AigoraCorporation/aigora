# ADR-006 — Use Exporter Strategy Registry

## Status
Accepted

## Context

The Curriculum Graph must support multiple export formats.

Hardcoding export format conditionals inside `ExportGraphUseCase` would make the use case grow every time a new format is introduced.

## Decision

Export behavior is implemented using a strategy registry.

The application depends on the `CurriculumGraphExporter` port.

Concrete exporters include:

- CSV exporter
- JSON exporter
- YAML exporter

`CurriculumGraphExporterRegistry` resolves the exporter for the requested format.

## Consequences

### Positive

- `ExportGraphUseCase` stays format-agnostic
- new formats can be added with minimal use case changes
- exporters can be tested independently
- strategy resolution is centralized

### Negative

- a registry/factory must be configured
- unsupported formats require explicit error handling

## Constraints

- format-specific writing belongs to infrastructure
- unsupported format errors must be defined in dedicated error modules
- the use case must not contain CSV/JSON/YAML conditionals
