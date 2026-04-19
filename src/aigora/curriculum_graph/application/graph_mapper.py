from __future__ import annotations

from typing import Any

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.node import Node

from .mapper_errors import (
    InvalidEdgePayloadError,
    InvalidGraphPayloadError,
    InvalidNodePayloadError,
    InvalidProfilePayloadError,
)


class GraphMapper:
    def map_graph(self, payload: dict[str, Any]) -> CurriculumGraph:
        if not isinstance(payload, dict):
            raise InvalidGraphPayloadError("Graph payload must be a dictionary.")

        nodes_payload = payload.get("nodes")
        edges_payload = payload.get("edges")
        profiles_payload = payload.get("profiles", [])

        if not isinstance(nodes_payload, list):
            raise InvalidGraphPayloadError("Graph payload field 'nodes' must be a list.")
        if not isinstance(edges_payload, list):
            raise InvalidGraphPayloadError("Graph payload field 'edges' must be a list.")
        if not isinstance(profiles_payload, list):
            raise InvalidGraphPayloadError("Graph payload field 'profiles' must be a list.")

        graph = CurriculumGraph()

        for raw_node in nodes_payload:
            graph.add_node(self.map_node(raw_node))

        for raw_edge in edges_payload:
            graph.add_edge(self.map_edge(raw_edge))

        for raw_profile in profiles_payload:
            graph.add_profile(self.map_profile(raw_profile))

        return graph

    def map_node(self, payload: dict[str, Any]) -> Node:
        if not isinstance(payload, dict):
            raise InvalidNodePayloadError("Node payload must be a dictionary.")

        mastery_payload = payload.get("mastery")
        if not isinstance(mastery_payload, dict):
            raise InvalidNodePayloadError("Node field 'mastery' must be a dictionary.")

        levels_payload = mastery_payload.get("levels")
        if not isinstance(levels_payload, list):
            raise InvalidNodePayloadError("Node mastery field 'levels' must be a list.")

        criteria_by_level: dict[MasteryLevel, MasteryCriterion] = {}

        for raw_level in levels_payload:
            if not isinstance(raw_level, dict):
                raise InvalidNodePayloadError(
                    "Each mastery level entry must be a dictionary."
                )

            try:
                level = MasteryLevel(raw_level["level"])
            except KeyError as exc:
                raise InvalidNodePayloadError(
                    "Each mastery level entry must contain 'level'."
                ) from exc
            except ValueError as exc:
                raise InvalidNodePayloadError(
                    f"Invalid mastery level value: {raw_level.get('level')}"
                ) from exc

            try:
                description = raw_level["description"]
            except KeyError as exc:
                raise InvalidNodePayloadError(
                    "Each mastery level entry must contain 'description'."
                ) from exc

            criteria_by_level[level] = MasteryCriterion(
                level=level,
                description=description,
            )

        mastery_scale = MasteryScale(criteria_by_level=criteria_by_level)

        try:
            return Node(
                id=payload["id"],
                name=payload["name"],
                domain=payload["domain"],
                description=payload["description"],
                mastery_criteria=mastery_scale,
                error_taxonomy=payload.get("error_taxonomy", []),
                prerequisite_ids=payload.get("prerequisites", []),
                regression_ids=payload.get("regressions", []),
            )
        except KeyError as exc:
            raise InvalidNodePayloadError(
                f"Missing required node field: {exc.args[0]}"
            ) from exc
        except ValueError as exc:
            raise InvalidNodePayloadError(str(exc)) from exc

    def map_edge(self, payload: dict[str, Any]) -> Edge:
        if not isinstance(payload, dict):
            raise InvalidEdgePayloadError("Edge payload must be a dictionary.")

        try:
            edge_type = EdgeType(payload["type"])
        except KeyError as exc:
            raise InvalidEdgePayloadError("Missing required edge field: type") from exc
        except ValueError as exc:
            raise InvalidEdgePayloadError(
                f"Invalid edge type: {payload.get('type')}"
            ) from exc

        try:
            return Edge(
                type=edge_type,
                source=payload["source"],
                target=payload["target"],
            )
        except KeyError as exc:
            raise InvalidEdgePayloadError(
                f"Missing required edge field: {exc.args[0]}"
            ) from exc
        except ValueError as exc:
            raise InvalidEdgePayloadError(str(exc)) from exc

    def map_profile(self, payload: dict[str, Any]) -> CurriculumProfile:
        if not isinstance(payload, dict):
            raise InvalidProfilePayloadError("Profile payload must be a dictionary.")

        mastery_targets_payload = payload.get("mastery_targets", {})
        if not isinstance(mastery_targets_payload, dict):
            raise InvalidProfilePayloadError(
                "Profile field 'mastery_targets' must be a dictionary."
            )

        mastery_targets: dict[str, MasteryLevel] = {}
        for node_id, level_value in mastery_targets_payload.items():
            try:
                mastery_targets[node_id] = MasteryLevel(level_value)
            except ValueError as exc:
                raise InvalidProfilePayloadError(
                    f"Invalid mastery target level for node '{node_id}': {level_value}"
                ) from exc

        try:
            return CurriculumProfile(
                id=payload["id"],
                name=payload["name"],
                required_nodes=set(payload.get("required_nodes", [])),
                mastery_targets=mastery_targets,
                node_weights=payload.get("node_weights", {}),
                progression_path=payload.get("progression_path", []),
                exam_skill_overlay=payload.get("exam_skill_overlay", []),
            )
        except KeyError as exc:
            raise InvalidProfilePayloadError(
                f"Missing required profile field: {exc.args[0]}"
            ) from exc
        except ValueError as exc:
            raise InvalidProfilePayloadError(str(exc)) from exc