from __future__ import annotations

from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_context import (
    GraphLoadingContext,
)
from aigora.curriculum_graph.application.validation.curriculum_graph_version_validator import (
    CurriculumGraphVersionValidator,
)


class ValidateVersionStep:
    """Validate graph versioning invariants."""

    def __init__(self, version_validator: CurriculumGraphVersionValidator) -> None:
        self._version_validator = version_validator

    def execute(self, context: GraphLoadingContext) -> None:
        if context.graph is None:
            raise ValueError("Graph must be assembled before version validation.")

        self._version_validator.validate(context.graph)
