from __future__ import annotations

from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_pipeline import (
    GraphLoadingPipeline,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.steps.assemble_graph_step import (
    AssembleGraphStep,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.steps.map_graph_step import (
    MapGraphStep,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.steps.parse_graph_step import (
    ParseGraphStep,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.steps.validate_graph_step import (
    ValidateGraphStep,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.steps.validate_schema_step import (
    ValidateSchemaStep,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.steps.validate_version_step import (
    ValidateVersionStep,
)
from aigora.curriculum_graph.application.validation.curriculum_graph_validator import CurriculumGraphValidator
from aigora.curriculum_graph.application.validation.curriculum_graph_version_validator import (
    CurriculumGraphVersionValidator,
)
from aigora.curriculum_graph.infrastructure.files.assembling.curriculum_graph_assembler import (
    CurriculumGraphAssembler,
)
from aigora.curriculum_graph.infrastructure.files.mapping.curriculum_graph_mapper import CurriculumGraphMapper
from aigora.curriculum_graph.infrastructure.files.parsing.curriculum_graph_file_parser import CurriculumGraphFileParser
from aigora.curriculum_graph.infrastructure.files.validation.curriculum_graph_schema_validator import (
    CurriculumGraphSchemaValidator,
)


def build_file_curriculum_graph_loading_pipeline() -> GraphLoadingPipeline:
    """Compose the file-based graph loading pipeline using concrete adapters."""

    return GraphLoadingPipeline(
        steps=(
            ParseGraphStep(CurriculumGraphFileParser()),
            ValidateSchemaStep(CurriculumGraphSchemaValidator()),
            MapGraphStep(CurriculumGraphMapper()),
            AssembleGraphStep(CurriculumGraphAssembler()),
            ValidateGraphStep(CurriculumGraphValidator()),
            ValidateVersionStep(CurriculumGraphVersionValidator()),
        )
    )
