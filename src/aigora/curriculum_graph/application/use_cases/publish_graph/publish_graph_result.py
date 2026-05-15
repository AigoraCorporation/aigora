from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aigora.curriculum_graph.application.use_cases.export_graph import CurriculumGraphExportFormat


@dataclass(frozen=True)
class PublishGraphResult:
    """Output model returned by PublishGraphUseCase."""

    graph_version: str
    nodes_published: int
    edges_published: int
    profiles_published: int
    graph_exported: bool = False
    export_format: CurriculumGraphExportFormat | None = None
    exported_files: dict[str, Path] | None = None
