from __future__ import annotations

from pathlib import Path

from aigora.curriculum_graph.application.errors import LoadGraphError

from .load_graph_command import LoadGraphCommand
from .load_graph_result import LoadGraphResult
from .pipeline import GraphLoadingContext, GraphLoadingPipeline


class LoadGraphUseCase:
    """Application use case responsible for loading a CurriculumGraph from a file."""

    def __init__(self, pipeline: GraphLoadingPipeline) -> None:
        self._pipeline = pipeline

    def execute(self, command: LoadGraphCommand) -> LoadGraphResult:
        file_path = Path(command.file_path)

        try:
            context = GraphLoadingContext(file_path=file_path)
            graph = self._pipeline.execute(context)

            return LoadGraphResult(
                graph=graph,
                nodes_loaded=len(graph.nodes),
                edges_loaded=len(graph.edges),
                profiles_loaded=len(graph.profiles),
                version=graph.version or "",
            )

        except Exception as exc:
            raise LoadGraphError(
                f"Failed to load CurriculumGraph from file: {file_path}"
            ) from exc
