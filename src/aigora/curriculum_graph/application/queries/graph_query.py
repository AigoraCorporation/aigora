from __future__ import annotations

from collections import deque
from collections.abc import Iterable

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType
from aigora.curriculum_graph.domain.node import Node
from aigora.curriculum_graph.application.queries.query_errors import NodeNotFoundError, PathNotFoundError

class GraphQuery:
    """Read-only query interface for in-memory CurriculumGraph traversal.

    Responsibilities:
    - Retrieve prerequisite nodes for a given node
    - Retrieve dependent nodes for a given node
    - Derive a learning path between two nodes

    This component does not mutate the graph and does not depend on
    persistence or external graph engines.
    """

    def __init__(self, graph: CurriculumGraph) -> None:
        self._graph = graph

    def get_node(self, node_id: str) -> Node:
        self._ensure_node_exists(node_id)
        return self._graph.get_node(node_id)

    def get_prerequisites(
        self,
        node_id: str,
        *,
        include_soft: bool = True,
    ) -> list[Node]:
        """Return direct prerequisite nodes for the given node.

        By default, both hard and soft prerequisites are included.
        """
        self._ensure_node_exists(node_id)

        allowed_types = {EdgeType.HARD_PREREQUISITE}
        if include_soft:
            allowed_types.add(EdgeType.SOFT_PREREQUISITE)

        prerequisite_ids = [
            edge.source
            for edge in self._graph.incoming_edges(node_id)
            if edge.type in allowed_types
        ]

        return [self._graph.get_node(prereq_id) for prereq_id in prerequisite_ids]

    def get_dependents(
        self,
        node_id: str,
        *,
        include_soft: bool = True,
    ) -> list[Node]:
        """Return direct dependent nodes for the given node.

        By default, both hard and soft prerequisites are included.
        """
        self._ensure_node_exists(node_id)

        allowed_types = {EdgeType.HARD_PREREQUISITE}
        if include_soft:
            allowed_types.add(EdgeType.SOFT_PREREQUISITE)

        dependent_ids = [
            edge.target
            for edge in self._graph.outgoing_edges(node_id)
            if edge.type in allowed_types
        ]

        return [self._graph.get_node(dependent_id) for dependent_id in dependent_ids]

    def get_learning_path(
        self,
        start_node_id: str,
        target_node_id: str,
        *,
        include_soft: bool = True,
    ) -> list[Node]:
        """Return one shortest path from start node to target node.

        Uses BFS over prerequisite edges:
        source -> target
        """
        self._ensure_node_exists(start_node_id)
        self._ensure_node_exists(target_node_id)

        if start_node_id == target_node_id:
            return [self._graph.get_node(start_node_id)]

        adjacency = self._build_adjacency(include_soft=include_soft)

        queue: deque[str] = deque([start_node_id])
        parents: dict[str, str | None] = {start_node_id: None}

        while queue:
            current = queue.popleft()

            for neighbor in adjacency.get(current, []):
                if neighbor in parents:
                    continue

                parents[neighbor] = current

                if neighbor == target_node_id:
                    return self._reconstruct_path(parents, target_node_id)

                queue.append(neighbor)

        raise PathNotFoundError(
            f"No learning path found from {start_node_id!r} to {target_node_id!r}."
        )

    def _build_adjacency(self, *, include_soft: bool) -> dict[str, list[str]]:
        allowed_types = {EdgeType.HARD_PREREQUISITE}
        if include_soft:
            allowed_types.add(EdgeType.SOFT_PREREQUISITE)

        adjacency: dict[str, list[str]] = {}

        for edge in self._graph.edges:
            if edge.type not in allowed_types:
                continue

            adjacency.setdefault(edge.source, []).append(edge.target)

        return adjacency

    def _reconstruct_path(
        self,
        parents: dict[str, str | None],
        target_node_id: str,
    ) -> list[Node]:
        path_ids: list[str] = []
        current: str | None = target_node_id

        while current is not None:
            path_ids.append(current)
            current = parents[current]

        path_ids.reverse()
        return [self._graph.get_node(node_id) for node_id in path_ids]

    def _ensure_node_exists(self, node_id: str) -> None:
        if node_id not in self._graph.nodes:
            raise NodeNotFoundError(f"Node not found in CurriculumGraph: {node_id!r}")