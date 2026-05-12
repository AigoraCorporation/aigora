from __future__ import annotations

from aigora.curriculum_graph.application.ports.curriculum_graph_schema_validator import (
    CurriculumGraphSchemaValidatorPort,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_context import (
    GraphLoadingContext,
)


class ValidateSchemaStep:
    """Validate the raw graph payload shape before mapping domain objects."""

    def __init__(self, schema_validator: CurriculumGraphSchemaValidatorPort) -> None:
        self._schema_validator = schema_validator

    def execute(self, context: GraphLoadingContext) -> None:
        if context.payload is None:
            raise ValueError("Graph payload must be parsed before schema validation.")

        self._schema_validator.validate(context.payload)
