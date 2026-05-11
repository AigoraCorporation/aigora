from __future__ import annotations

from aigora.curriculum_graph.application.ports.curriculum_graph_assembler import CurriculumGraphAssemblerPort
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_context import (
    GraphLoadingContext,
)


class AssembleGraphStep:
    """Assemble mapped domain objects into a coherent CurriculumGraph."""

    def __init__(self, assembler: CurriculumGraphAssemblerPort) -> None:
        self._assembler = assembler

    def execute(self, context: GraphLoadingContext) -> None:
        context.graph = self._assembler.assemble(
            nodes=context.nodes,
            edges=context.edges,
            profiles=context.profiles,
            version=context.version,
        )
