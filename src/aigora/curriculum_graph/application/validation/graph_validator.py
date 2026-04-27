from __future__ import annotations

import re
from collections import defaultdict

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.node import Node

from .validation_errors import (
    CyclicDependencyError,
    InvalidEdgeReferenceError,
    InvalidNodeIdFormatError,
    InvalidNodeMasteryDefinitionError,
    InvalidProfileIdFormatError,
    InvalidProfileMasteryTargetError,
    InvalidProfileProgressionPathError,
    InvalidProfileReferenceError,
    InvalidProfileWeightError,
)

_NODE_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*\.[a-z0-9]+(?:-[a-z0-9]+)*$")
_PROFILE_ID_PATTERN = re.compile(r"^profile\.[a-z0-9]+(?:-[a-z0-9]+)*$")


class GraphValidator:
    """Validates structural integrity of a CurriculumGraph.

    This validator focuses on the automatable structural checks documented
    for the Curriculum Graph. It assumes domain objects have already been
    created and assembled successfully.
    """

    def validate(self, graph: CurriculumGraph) -> None:
        self._validate_node_id_format(graph)
        self._validate_profile_id_format(graph)
        self._validate_edge_references(graph)
        self._validate_node_mastery_definitions(graph)
        self._validate_profile_references(graph)
        self._validate_profile_mastery_targets(graph)
        self._validate_profile_weights(graph)
        self._validate_profile_progression_paths(graph)
        self._validate_prerequisite_cycles(graph)

    def _validate_node_id_format(self, graph: CurriculumGraph) -> None:
        for node in graph.nodes.values():
            if not _NODE_ID_PATTERN.fullmatch(node.id):
                raise InvalidNodeIdFormatError(
                    f"Node id does not conform to the expected format: {node.id!r}"
                )

    def _validate_profile_id_format(self, graph: CurriculumGraph) -> None:
        for profile in graph.profiles.values():
            if not _PROFILE_ID_PATTERN.fullmatch(profile.id):
                raise InvalidProfileIdFormatError(
                    f"Profile id does not conform to the expected format: {profile.id!r}"
                )

    def _validate_edge_references(self, graph: CurriculumGraph) -> None:
        for edge in graph.edges:
            if edge.source not in graph.nodes:
                raise InvalidEdgeReferenceError(
                    f"Edge source references unknown node: {edge.source!r}"
                )
            if edge.target not in graph.nodes:
                raise InvalidEdgeReferenceError(
                    f"Edge target references unknown node: {edge.target!r}"
                )

    def _validate_node_mastery_definitions(self, graph: CurriculumGraph) -> None:
        for node in graph.nodes.values():
            self._validate_node_mastery_definition(node)

    def _validate_node_mastery_definition(self, node: Node) -> None:
        criteria = node.mastery_criteria.criteria_by_level

        if not criteria:
            raise InvalidNodeMasteryDefinitionError(
                f"Node {node.id!r} must define at least one mastery level."
            )

        for level, criterion in criteria.items():
            if criterion.level != level:
                raise InvalidNodeMasteryDefinitionError(
                    f"Node {node.id!r} has inconsistent mastery criterion for level {level!r}."
                )

            if not criterion.description.strip():
                raise InvalidNodeMasteryDefinitionError(
                    f"Node {node.id!r} has an empty mastery description for level {level!r}."
                )

    def _validate_profile_references(self, graph: CurriculumGraph) -> None:
        for profile in graph.profiles.values():
            for node_id in profile.referenced_node_ids():
                if node_id not in graph.nodes:
                    raise InvalidProfileReferenceError(
                        f"Profile {profile.id!r} references unknown node: {node_id!r}"
                    )

    def _validate_profile_mastery_targets(self, graph: CurriculumGraph) -> None:
        for profile in graph.profiles.values():
            for node_id, mastery_level in profile.mastery_targets.items():
                node = graph.nodes.get(node_id)
                if node is None:
                    raise InvalidProfileReferenceError(
                        f"Profile {profile.id!r} references unknown node in mastery_targets: {node_id!r}"
                    )

                if mastery_level == MasteryLevel.UNEXPOSED:
                    raise InvalidProfileMasteryTargetError(
                        f"Profile {profile.id!r} defines invalid mastery target "
                        f"{mastery_level!r} for node {node_id!r}. "
                        "UNEXPOSED is not a valid curriculum target."
                    )

                if not node.mastery_criteria.has_level(mastery_level):
                    raise InvalidProfileMasteryTargetError(
                        f"Profile {profile.id!r} targets unsupported mastery level "
                        f"{mastery_level!r} for node {node_id!r}"
                    )

    def _validate_profile_weights(self, graph: CurriculumGraph) -> None:
        for profile in graph.profiles.values():
            for node_id, weight in profile.node_weights.items():
                if node_id not in graph.nodes:
                    raise InvalidProfileReferenceError(
                        f"Profile {profile.id!r} assigns weight to unknown node: {node_id!r}"
                    )

                if weight <= 0:
                    raise InvalidProfileWeightError(
                        f"Profile {profile.id!r} defines invalid weight {weight!r} "
                        f"for node {node_id!r}. Weights must be strictly positive."
                    )

    def _validate_profile_progression_paths(self, graph: CurriculumGraph) -> None:
        hard_prerequisites = self._build_hard_prerequisite_map(graph)

        for profile in graph.profiles.values():
            path = profile.progression_path

            for node_id in path:
                if node_id not in graph.nodes:
                    raise InvalidProfileProgressionPathError(
                        f"Profile {profile.id!r} progression path references unknown node: {node_id!r}"
                    )

            positions = {node_id: index for index, node_id in enumerate(path)}

            for node_id in path:
                for prerequisite_id in hard_prerequisites[node_id]:
                    if prerequisite_id in positions and positions[prerequisite_id] > positions[node_id]:
                        raise InvalidProfileProgressionPathError(
                            f"Profile {profile.id!r} progression path violates prerequisite order: "
                            f"{prerequisite_id!r} must appear before {node_id!r}"
                        )

    def _validate_prerequisite_cycles(self, graph: CurriculumGraph) -> None:
        adjacency = self._build_prerequisite_adjacency(graph)

        visited: set[str] = set()
        visiting: set[str] = set()

        def dfs(node_id: str) -> None:
            if node_id in visiting:
                raise CyclicDependencyError(
                    f"Cyclic prerequisite dependency detected at node: {node_id!r}"
                )

            if node_id in visited:
                return

            visiting.add(node_id)
            for neighbor in adjacency[node_id]:
                dfs(neighbor)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in graph.nodes:
            if node_id not in visited:
                dfs(node_id)

    def _build_prerequisite_adjacency(self, graph: CurriculumGraph) -> dict[str, list[str]]:
        adjacency: dict[str, list[str]] = defaultdict(list)

        for edge in graph.edges:
            if edge.type in {EdgeType.HARD_PREREQUISITE, EdgeType.SOFT_PREREQUISITE}:
                adjacency[edge.source].append(edge.target)

        return adjacency

    def _build_hard_prerequisite_map(self, graph: CurriculumGraph) -> dict[str, set[str]]:
        prerequisites: dict[str, set[str]] = defaultdict(set)

        for edge in graph.edges:
            if edge.type == EdgeType.HARD_PREREQUISITE:
                prerequisites[edge.target].add(edge.source)

        return prerequisites