from __future__ import annotations

from pathlib import Path

from aigora.curriculum_graph.application.use_cases.export_graph import CurriculumGraphExporterRegistry
from aigora.curriculum_graph.application.use_cases.load_graph import (
    LoadGraphCommand,
    LoadGraphUseCase,
)
from aigora.curriculum_graph.domain.repositories.curriculum_graph_repository import CurriculumGraphRepository

from .publish_graph_command import PublishGraphCommand
from .publish_graph_result import PublishGraphResult


class PublishGraphUseCase:
    """Application use case responsible for publishing a CurriculumGraph."""

    def __init__(
        self,
        loader: LoadGraphUseCase,
        repository: CurriculumGraphRepository,
        exporter_registry: CurriculumGraphExporterRegistry | None = None,
    ) -> None:
        self._loader = loader
        self._repository = repository
        self._exporter_registry = exporter_registry

    def execute(self, command: PublishGraphCommand) -> PublishGraphResult:
        load_result = self._loader.execute(LoadGraphCommand(file_path=command.file_path))
        graph = load_result.graph

        exported_files: dict[str, Path] = {}
        export_format = command.normalized_export_format()

        if command.export_graph:
            if self._exporter_registry is None:
                raise ValueError(
                    "export_graph=True requires an exporter registry to be provided at construction time."
                )
            if command.export_output_dir is None:
                raise ValueError("export_output_dir must be provided when export_graph=True.")
            exporter = self._exporter_registry.get(export_format)
            exported_files = exporter.export(graph, command.export_output_dir)

        self._repository.apply_schema()
        self._repository.persist(graph)
        self._repository.validate(graph)

        return PublishGraphResult(
            graph_version=graph.version or "",
            nodes_published=len(graph.nodes),
            edges_published=len(graph.edges),
            profiles_published=len(graph.profiles),
            graph_exported=command.export_graph,
            export_format=export_format if command.export_graph else None,
            exported_files=exported_files,
        )
