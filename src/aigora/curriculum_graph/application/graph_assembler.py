from __future__ import annotations

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.node import Node

from .assembler_errors import (
    DuplicateNodeError,
    DuplicateProfileError,
    UnresolvedNodeReferenceError,
)


class GraphAssembler:
    """Consolidates mapped domain objects into a final in-memory CurriculumGraph.

    Responsibilities:
    - Detect duplicate node and profile ids before assembly.
    - Validate that all edge endpoints and profile node references resolve to
      known nodes within the assembled graph.
    - Produce a deterministic, coherent CurriculumGraph ready for validation
      and querying by downstream layers.

    This class is deliberately independent from file reading, syntax parsing,
    and raw payload mapping concerns.
    """

    def assemble(
        self,
        nodes: list[Node],
        edges: list[Edge],
        profiles: list[CurriculumProfile],
        version: str | None = None,
    ) -> CurriculumGraph:
        node_ids = self._collect_node_ids(nodes)
        self._validate_edges(edges, node_ids)
        self._validate_profiles(profiles, node_ids)

        graph = CurriculumGraph(version=version)

        for node in nodes:
            graph.add_node(node)

        for edge in edges:
            graph.add_edge(edge)

        for profile in profiles:
            graph.add_profile(profile)

        return graph

    # ── Internal validation ───────────────────────────────────────────────────

    def _collect_node_ids(self, nodes: list[Node]) -> set[str]:
        seen: set[str] = set()
        for node in nodes:
            if node.id in seen:
                raise DuplicateNodeError(f"Duplicate node id: {node.id}")
            seen.add(node.id)
        return seen

    def _validate_edges(self, edges: list[Edge], node_ids: set[str]) -> None:
        for edge in edges:
            if edge.source not in node_ids:
                raise UnresolvedNodeReferenceError(
                    f"Edge source references unknown node: {edge.source!r}"
                )
            if edge.target not in node_ids:
                raise UnresolvedNodeReferenceError(
                    f"Edge target references unknown node: {edge.target!r}"
                )

    def _validate_profiles(
        self, profiles: list[CurriculumProfile], node_ids: set[str]
    ) -> None:
        seen: set[str] = set()
        for profile in profiles:
            if profile.id in seen:
                raise DuplicateProfileError(f"Duplicate profile id: {profile.id}")
            seen.add(profile.id)

            for node_id in profile.referenced_node_ids():
                if node_id not in node_ids:
                    raise UnresolvedNodeReferenceError(
                        f"Profile {profile.id!r} references unknown node: {node_id!r}"
                    )
