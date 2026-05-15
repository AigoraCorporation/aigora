from __future__ import annotations

from aigora.curriculum_graph.application.ports.curriculum_graph_file_parser import CurriculumGraphFileParserPort
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_context import (
    GraphLoadingContext,
)


class ParseGraphStep:
    """Parse the source file into a raw graph payload."""

    def __init__(self, parser: CurriculumGraphFileParserPort) -> None:
        self._parser = parser

    def execute(self, context: GraphLoadingContext) -> None:
        context.payload = self._parser.parse_file(context.file_path)
