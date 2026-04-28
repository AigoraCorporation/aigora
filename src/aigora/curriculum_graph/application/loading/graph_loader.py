from __future__ import annotations

from pathlib import Path
from typing import Any

from aigora.curriculum_graph.application.assembling.graph_assembler import GraphAssembler
from aigora.curriculum_graph.application.loading.loader_errors import GraphLoaderError
from aigora.curriculum_graph.application.mapping.graph_mapper import GraphMapper
from aigora.curriculum_graph.application.parsing.graph_parser import GraphParser
from aigora.curriculum_graph.application.validation.graph_schema_validator import (
    GraphSchemaValidator,
)
from aigora.curriculum_graph.application.validation.graph_validator import GraphValidator
from aigora.curriculum_graph.application.validation.graph_version_validator import (
    GraphVersionValidator,
)
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph


class GraphLoader:
    """Loads a CurriculumGraph from a file-based source.

    Responsibilities:
    - Read a graph definition file through GraphParser.
    - Validate raw payload structure through GraphSchemaValidator.
    - Map parsed payload data into domain objects through GraphMapper.
    - Assemble the final in-memory CurriculumGraph through GraphAssembler.
    - Validate the assembled graph through GraphValidator.
    - Validate graph version metadata through GraphVersionValidator.

    This class acts as the application-level entry point for the file-based
    Curriculum Graph loading pipeline.
    """

    def __init__(
        self,
        parser: GraphParser | None = None,
        schema_validator: GraphSchemaValidator | None = None,
        mapper: GraphMapper | None = None,
        assembler: GraphAssembler | None = None,
        graph_validator: GraphValidator | None = None,
        version_validator: GraphVersionValidator | None = None,
    ) -> None:
        self._parser = parser or GraphParser()
        self._schema_validator = schema_validator or GraphSchemaValidator()
        self._mapper = mapper or GraphMapper()
        self._assembler = assembler or GraphAssembler()
        self._graph_validator = graph_validator or GraphValidator()
        self._version_validator = version_validator or GraphVersionValidator()

    def load(self, file_path: str | Path) -> CurriculumGraph:
        try:
            payload = self._parser.parse_file(file_path)

            self._schema_validator.validate(payload)

            nodes = self._map_nodes(payload)
            edges = self._map_edges(payload)
            profiles = self._map_profiles(payload)
            version = self._map_version(payload)

            graph = self._assembler.assemble(
                nodes=nodes,
                edges=edges,
                profiles=profiles,
                version=version,
            )

            self._graph_validator.validate(graph)
            self._version_validator.validate(graph)

            return graph
        except Exception as exc:
            raise GraphLoaderError(
                f"Failed to load CurriculumGraph from file: {file_path}"
            ) from exc

    def _map_nodes(self, payload: dict[str, Any]):
        return [self._mapper.map_node(node_payload) for node_payload in payload["nodes"]]

    def _map_edges(self, payload: dict[str, Any]):
        return [self._mapper.map_edge(edge_payload) for edge_payload in payload["edges"]]

    def _map_profiles(self, payload: dict[str, Any]):
        return [
            self._mapper.map_profile(profile_payload)
            for profile_payload in payload.get("profiles", [])
        ]

    def _map_version(self, payload: dict[str, Any]) -> str | None:
        version = payload.get("version")
        if version is not None and not isinstance(version, str):
            from aigora.curriculum_graph.application.mapping.mapper_errors import (
                InvalidGraphPayloadError,
            )

            raise InvalidGraphPayloadError(
                "Graph payload field 'version' must be a string."
            )
        return version