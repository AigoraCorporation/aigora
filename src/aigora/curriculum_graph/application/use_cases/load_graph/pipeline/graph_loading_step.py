from __future__ import annotations

from typing import Protocol

from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_context import (
    GraphLoadingContext,
)


class GraphLoadingStep(Protocol):
    """Pipeline step contract for loading a CurriculumGraph."""

    def execute(self, context: GraphLoadingContext) -> None:
        """Apply this step to the shared loading context."""
        ...
