from __future__ import annotations

import json
from typing import Any

from aigora.curriculum_graph.application.errors.read_graph_errors import GraphUnavailableError
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.entities.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.entities.edge import Edge
from aigora.curriculum_graph.domain.entities.node import Node
from aigora.curriculum_graph.domain.enums.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.value_objects.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.infrastructure.neo4j.errors import Neo4jClientError
from aigora.curriculum_graph.infrastructure.neo4j.neo4j_client import Neo4jClient

_ACTIVE_VERSION = """
MATCH (m:GraphMetadata {key: 'active'})
RETURN m.graph_version AS graph_version
"""

_NODES = """
MATCH (n:Concept {graph_version: $graph_version})
RETURN n.id AS id, n.name AS name, n.domain AS domain, n.description AS description,
       n.mastery_criteria_json AS mastery_criteria_json, n.error_taxonomy AS error_taxonomy,
       n.prerequisite_ids AS prerequisite_ids, n.regression_ids AS regression_ids
ORDER BY n.id
"""

_EDGES = """
MATCH (s:Concept {graph_version: $graph_version})-[r:PREREQUISITE_OF {graph_version: $graph_version}]->
      (t:Concept {graph_version: $graph_version})
RETURN s.id AS source, t.id AS target, r.type AS type
ORDER BY source, target, type
"""

_PROFILES = """
MATCH (p:CurriculumProfile {graph_version: $graph_version})
RETURN p.id AS id, p.name AS name, p.required_nodes AS required_nodes,
       p.mastery_targets_json AS mastery_targets_json, p.node_weights_json AS node_weights_json,
       p.progression_path AS progression_path, p.exam_skill_overlay AS exam_skill_overlay
ORDER BY p.id
"""


class Neo4jCurriculumGraphReader:
    """Neo4j implementation of the `CurriculumGraphReader` port (ADR-007).

    Rebuilds the published snapshot: the version recorded in the
    `:GraphMetadata {key: 'active'}` node and every Concept, PREREQUISITE_OF
    relationship and CurriculumProfile stamped with that version.
    """

    def __init__(self, client: Neo4jClient) -> None:
        self._client = client

    def load_published(self) -> CurriculumGraph:
        try:
            rows = self._client.run(_ACTIVE_VERSION)
            version = rows[0]["graph_version"] if rows else None
            if not version:
                raise GraphUnavailableError("No published Curriculum Graph found in the graph store.")
            params = {"graph_version": version}
            node_rows = self._client.run(_NODES, params)
            edge_rows = self._client.run(_EDGES, params)
            profile_rows = self._client.run(_PROFILES, params)
        except Neo4jClientError as exc:
            raise GraphUnavailableError("The graph store is unreachable.") from exc

        try:
            return _build_graph(version, node_rows, edge_rows, profile_rows)
        except (KeyError, TypeError, ValueError) as exc:
            raise GraphUnavailableError(
                f"Published graph {version!r} is incomplete or invalid; republish it with the current "
                "publication pipeline."
            ) from exc


def _build_graph(
    version: str,
    node_rows: list[dict[str, Any]],
    edge_rows: list[dict[str, Any]],
    profile_rows: list[dict[str, Any]],
) -> CurriculumGraph:
    if not node_rows:
        raise ValueError("Published graph has no concepts.")
    graph = CurriculumGraph(version=version)
    for row in node_rows:
        graph.add_node(_build_node(row))
    for row in edge_rows:
        graph.add_edge(Edge(type=EdgeType(row["type"]), source=row["source"], target=row["target"]))
    for row in profile_rows:
        graph.add_profile(_build_profile(row))
    return graph


def _build_node(row: dict[str, Any]) -> Node:
    raw_criteria = row.get("mastery_criteria_json")
    if not raw_criteria:
        raise ValueError(f"Concept {row.get('id')!r} has no mastery criteria.")
    criteria = {}
    for item in json.loads(raw_criteria):
        level = MasteryLevel(int(item["level"]))
        criteria[level] = MasteryCriterion(level=level, description=item["description"])
    return Node(
        id=row["id"],
        name=row["name"],
        domain=row["domain"],
        description=row["description"],
        mastery_criteria=MasteryScale(criteria_by_level=criteria),
        error_taxonomy=list(row.get("error_taxonomy") or []),
        prerequisite_ids=list(row.get("prerequisite_ids") or []),
        regression_ids=list(row.get("regression_ids") or []),
    )


def _build_profile(row: dict[str, Any]) -> CurriculumProfile:
    mastery_targets = {
        node_id: MasteryLevel(int(level))
        for node_id, level in json.loads(row.get("mastery_targets_json") or "{}").items()
    }
    return CurriculumProfile(
        id=row["id"],
        name=row["name"],
        required_nodes=set(row.get("required_nodes") or []),
        mastery_targets=mastery_targets,
        node_weights={k: float(v) for k, v in json.loads(row.get("node_weights_json") or "{}").items()},
        progression_path=list(row.get("progression_path") or []),
        exam_skill_overlay=list(row.get("exam_skill_overlay") or []),
    )
