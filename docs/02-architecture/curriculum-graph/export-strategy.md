# Curriculum Graph — Export Strategy

## Purpose

This document explains how Curriculum Graph export is implemented using a strategy registry/factory.

The goal is to support multiple export formats without changing the `ExportGraphUseCase` whenever a new format is added.

---

## Supported Formats

The current supported export formats are:

- CSV
- JSON
- YAML

The selected format is represented by `CurriculumGraphExportFormat`.

---

## Strategy Pattern

Each export format is implemented as a separate exporter strategy.

```text
CurriculumGraphExporter
  ↑
CsvCurriculumGraphExporter
JsonCurriculumGraphExporter
YamlCurriculumGraphExporter
```

The use case depends on the exporter abstraction, not on specific formats.

---

## Registry / Factory

`CurriculumGraphExporterRegistry` resolves the correct exporter for a requested format.

```text
ExportGraphUseCase
  ↓
CurriculumGraphExporterRegistry
  ↓
CurriculumGraphExporter
```

The registry acts as a strategy resolver and factory.

---

## Export Flow

```text
ExportGraphCommand
  ↓
ExportGraphUseCase
  ↓
CurriculumGraphExporterRegistry
  ↓
format-specific exporter
  ↓
ExportGraphResult
```

---

## Extending Export Formats

To add a new export format:

1. Add a new value to `CurriculumGraphExportFormat`.
2. Implement a new `CurriculumGraphExporter` adapter.
3. Register the exporter in the registry wiring.
4. Add unit tests for the new exporter and registry resolution.

The `ExportGraphUseCase` should not need to change.

---

## Error Handling

Unsupported export formats should raise an application-level export error.

The error must not be defined inside the registry class body. Error classes belong in dedicated error modules.

---

## Why This Matters

The exporter strategy keeps export behavior open for extension and closed for modification.

This avoids spreading format-specific conditionals across the application layer.

---

## Summary

The export architecture uses:

- a format enum
- exporter port
- concrete exporter strategies
- registry/factory resolution
- explicit command/result use case contract
