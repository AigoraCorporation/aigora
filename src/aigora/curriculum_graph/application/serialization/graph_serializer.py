from __future__ import annotations

import json
from typing import Any

import yaml

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.mastery import MasteryScale
from aigora.curriculum_graph.domain.node import Node
from aigora.curriculum_graph.application.serialization.serializer_errors import UnsupportedSerializationFormatError

SUPPORTED_FORMATS = {"json", "yaml"}


class GraphSerializer:
    """Serializes a CurriculumGraph into portable representations.

    Responsibilities:
    - Convert a CurriculumGraph domain object into a Python dictionary.
    - Serialize the dictionary into JSON or YAML string representations.

    This class is the reverse direction of the graph ingestion pipeline:
    domain → serializer → file representation
    """

    def to_dict(self, graph: CurriculumGraph) -> dict[str, Any]:
        return {
            "nodes": [self._serialize_node(node) for node in graph.nodes.values()],
            "edges": [self._serialize_edge(edge) for edge in graph.edges],
            "profiles": [
                self._serialize_profile(profile) for profile in graph.profiles.values()
            ],
        }

    def to_json(self, graph: CurriculumGraph) -> str:
        return json.dumps(self.to_dict(graph), indent=2)

    def to_yaml(self, graph: CurriculumGraph) -> str:
        return yaml.dump(self.to_dict(graph), default_flow_style=False, sort_keys=False)

    def serialize(self, graph: CurriculumGraph, fmt: str) -> str:
        normalized = fmt.lower().strip()
        if normalized not in SUPPORTED_FORMATS:
            raise UnsupportedSerializationFormatError(
                f"Unsupported serialization format: {fmt!r}. Supported: {sorted(SUPPORTED_FORMATS)}"
            )
        if normalized == "json":
            return self.to_json(graph)
        return self.to_yaml(graph)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _serialize_node(self, node: Node) -> dict[str, Any]:
        return {
            "id": node.id,
            "name": node.name,
            "domain": node.domain,
            "description": node.description,
            "mastery": self._serialize_mastery(node.mastery_criteria),
            "error_taxonomy": list(node.error_taxonomy),
            "prerequisites": list(node.prerequisite_ids),
            "regressions": list(node.regression_ids),
        }

    def _serialize_mastery(self, scale: MasteryScale) -> dict[str, Any]:
        return {
            "levels": [
                {"level": criterion.level.value, "description": criterion.description}
                for criterion in scale.criteria_by_level.values()
            ]
        }

    def _serialize_edge(self, edge: Edge) -> dict[str, Any]:
        return {
            "type": edge.type.value,
            "source": edge.source,
            "target": edge.target,
        }

    def _serialize_profile(self, profile: CurriculumProfile) -> dict[str, Any]:
        return {
            "id": profile.id,
            "name": profile.name,
            "required_nodes": sorted(profile.required_nodes),
            "mastery_targets": {
                node_id: level.value
                for node_id, level in profile.mastery_targets.items()
            },
            "node_weights": dict(profile.node_weights),
            "progression_path": list(profile.progression_path),
            "exam_skill_overlay": list(profile.exam_skill_overlay),
        }
