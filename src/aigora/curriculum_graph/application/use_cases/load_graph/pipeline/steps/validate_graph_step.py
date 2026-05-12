from __future__ import annotations

from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_context import (
    GraphLoadingContext,
)
from aigora.curriculum_graph.application.validation.curriculum_graph_validator import CurriculumGraphValidator


class ValidateGraphStep:
    """Validate domain-level graph consistency rules."""

    def __init__(self, validator: CurriculumGraphValidator) -> None:
        self._validator = validator

    def execute(self, context: GraphLoadingContext) -> None:
        if context.graph is None:
            raise ValueError("Graph must be assembled before graph validation.")

        self._validator.validate(context.graph)
