from __future__ import annotations

from aigora.curriculum_graph.application.ports.curriculum_graph_mapper import CurriculumGraphMapperPort
from aigora.curriculum_graph.application.errors.load_graph_errors import (
    InvalidGraphVersionError,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_context import (
    GraphLoadingContext,
)


class MapGraphStep:
    """Map raw graph payload data into domain entities and value objects."""

    def __init__(self, mapper: CurriculumGraphMapperPort) -> None:
        self._mapper = mapper

    def execute(self, context: GraphLoadingContext) -> None:
        if context.payload is None:
            raise ValueError("Graph payload must be parsed before mapping.")

        payload = context.payload
        context.nodes = [self._mapper.map_node(item) for item in payload["nodes"]]
        context.edges = [self._mapper.map_edge(item) for item in payload["edges"]]
        context.profiles = [
            self._mapper.map_profile(item) for item in payload.get("profiles", [])
        ]
        context.version = self._map_version(payload)

    def _map_version(self, payload: dict[str, object]) -> str:
        version = payload.get("version")

        if version is None:
            raise InvalidGraphVersionError("Graph payload field 'version' is required.")

        if not isinstance(version, str):
            raise InvalidGraphVersionError("Graph payload field 'version' must be a string.")

        return version
