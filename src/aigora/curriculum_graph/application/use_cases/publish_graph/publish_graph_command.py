from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aigora.curriculum_graph.application.use_cases.export_graph import CurriculumGraphExportFormat


@dataclass(frozen=True)
class PublishGraphCommand:
    """Input model for publishing a Curriculum Graph.

    This object carries the request data required by the application use case.
    It does not execute business logic or access infrastructure.
    """

    file_path: str | Path
    export_graph: bool = False
    export_output_dir: str | Path | None = None
    export_format: CurriculumGraphExportFormat | str = CurriculumGraphExportFormat.CSV

    def normalized_export_format(self) -> CurriculumGraphExportFormat:
        return CurriculumGraphExportFormat.from_value(self.export_format)
