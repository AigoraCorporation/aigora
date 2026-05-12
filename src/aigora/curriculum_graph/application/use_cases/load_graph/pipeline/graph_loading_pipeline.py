from __future__ import annotations

from collections.abc import Sequence

from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_context import (
    GraphLoadingContext,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_step import (
    GraphLoadingStep,
)
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph


class GraphLoadingPipeline:
    """Explicit application pipeline for loading a CurriculumGraph from a file."""

    def __init__(self, steps: Sequence[GraphLoadingStep]) -> None:
        self._steps = tuple(steps)

    def execute(self, context: GraphLoadingContext) -> CurriculumGraph:
        for step in self._steps:
            step.execute(context)

        if context.graph is None:
            raise ValueError("Graph loading pipeline finished without producing a graph.")

        return context.graph
