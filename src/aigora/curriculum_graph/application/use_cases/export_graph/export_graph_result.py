from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aigora.curriculum_graph.application.use_cases.export_graph.curriculum_graph_export_format import (
    CurriculumGraphExportFormat,
)


@dataclass(frozen=True)
class ExportGraphResult:
    """Output model returned by ExportGraphUseCase."""

    output_dir: Path
    output_format: CurriculumGraphExportFormat
    exported_files: dict[str, Path]
    nodes_exported: int
    edges_exported: int
    profiles_exported: int
