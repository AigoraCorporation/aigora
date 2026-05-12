from __future__ import annotations

from pathlib import Path

from .export_graph_command import ExportGraphCommand
from .export_graph_result import ExportGraphResult
from .curriculum_graph_exporter_registry import CurriculumGraphExporterRegistry


class ExportGraphUseCase:
    """Application use case responsible for exporting a CurriculumGraph."""

    def __init__(self, exporter_registry: CurriculumGraphExporterRegistry) -> None:
        self._exporter_registry = exporter_registry

    def execute(self, command: ExportGraphCommand) -> ExportGraphResult:
        output_format = command.normalized_output_format()
        output_dir = Path(command.output_dir)
        exporter = self._exporter_registry.get(output_format)

        exported_files = exporter.export(command.graph, output_dir)

        return ExportGraphResult(
            output_dir=output_dir,
            output_format=output_format,
            exported_files=exported_files,
            nodes_exported=len(command.graph.nodes),
            edges_exported=len(command.graph.edges),
            profiles_exported=len(command.graph.profiles),
        )
