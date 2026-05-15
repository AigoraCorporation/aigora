from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aigora.curriculum_graph.application.use_cases.export_graph.curriculum_graph_export_format import (
    CurriculumGraphExportFormat,
)
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph


@dataclass(frozen=True)
class ExportGraphCommand:
    """Input model for exporting an already loaded Curriculum Graph."""

    graph: CurriculumGraph
    output_dir: str | Path
    output_format: CurriculumGraphExportFormat | str = CurriculumGraphExportFormat.CSV

    def normalized_output_format(self) -> CurriculumGraphExportFormat:
        return CurriculumGraphExportFormat.from_value(self.output_format)
