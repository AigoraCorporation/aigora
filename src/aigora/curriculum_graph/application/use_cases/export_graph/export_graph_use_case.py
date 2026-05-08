from __future__ import annotations

from pathlib import Path

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.infrastructure.files.csv.graph_csv_exporter import GraphCsvExporter


class ExportGraphUseCase:
    """Application use case responsible for exporting a Curriculum Graph."""

    def __init__(self, csv_exporter: GraphCsvExporter | None = None) -> None:
        self._csv_exporter = csv_exporter or GraphCsvExporter()

    def export_csv(self, graph: CurriculumGraph, output_dir: str | Path) -> None:
        self._csv_exporter.export(graph, output_dir)
