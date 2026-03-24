from __future__ import annotations

from collections import deque
from typing import Optional

from ..domain.models import (
    CanonicalGraph,
    CanonicalNode,
    CurriculumProfile,
    PrerequisiteEdge,
)


class CurriculumGraphQueryService:
    """
    Executes queries against an already-loaded and validated CanonicalGraph.

    The graph is treated as immutable by this service. Internal indexes are
    built once at construction time to keep individual query costs low.
    This service is used internally by repository implementations — callers
    interact with CurriculumGraphRepository, not this class directly.
    """

    def __init__(self, graph: CanonicalGraph) -> None:
        self._graph = graph
        self._dependents: dict[str, list[str]] = self._build_dependents_index()

    # ── Index construction ─────────────────────────────────────────────────────

    def _build_dependents_index(self) -> dict[str, list[str]]:
        """Build a reverse map: node_id → list of node ids that directly depend on it."""
        index: dict[str, list[str]] = {nid: [] for nid in self._graph.nodes}
        for node in self._graph.nodes.values():
            for edge in node.prerequisite_ids:
                if edge.node_id in index:
                    index[edge.node_id].append(node.id)
        return index

    # ── Query methods ──────────────────────────────────────────────────────────

    def get_node(self, node_id: str) -> Optional[CanonicalNode]:
        return self._graph.nodes.get(node_id)

    def get_profile(self, profile_id: str) -> Optional[CurriculumProfile]:
        return self._graph.profiles.get(profile_id)

    def get_prerequisites(self, node_id: str) -> list[PrerequisiteEdge]:
        """Hard prerequisites are returned before soft prerequisites."""
        node = self._graph.nodes.get(node_id)
        if node is None:
            return []
        hard = [e for e in node.prerequisite_ids if e.edge_type.value == "hard"]
        soft = [e for e in node.prerequisite_ids if e.edge_type.value == "soft"]
        return hard + soft

    def get_dependents(self, node_id: str) -> list[str]:
        return list(self._dependents.get(node_id, []))

    def get_regression_targets(self, node_id: str) -> list[CanonicalNode]:
        node = self._graph.nodes.get(node_id)
        if node is None:
            return []
        return [
            self._graph.nodes[rid]
            for rid in node.regression_ids
            if rid in self._graph.nodes
        ]

    def is_reachable(self, from_id: str, to_id: str) -> bool:
        """
        BFS over prerequisite edges from `from_id`.
        Returns True if `to_id` is a transitive prerequisite of `from_id`.
        A node is not considered a prerequisite of itself.
        """
        if from_id == to_id:
            return False
        if from_id not in self._graph.nodes or to_id not in self._graph.nodes:
            return False
        visited: set[str] = set()
        queue: deque[str] = deque([from_id])
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            if current == to_id:
                return True
            node = self._graph.nodes.get(current)
            if node:
                for edge in node.prerequisite_ids:
                    if edge.node_id not in visited:
                        queue.append(edge.node_id)
        return False

    def topological_order(self, profile_id: str) -> list[str]:
        """
        Kahn's algorithm over the subgraph of nodes required by the profile.
        Returns node ids in topological order (prerequisites before dependents).
        Raises ValueError if the profile is not found.
        """
        profile = self._graph.profiles.get(profile_id)
        if profile is None:
            raise ValueError(f"Profile '{profile_id}' not found.")

        required = profile.required_node_ids()

        # Build in-degree and forward adjacency within the required subgraph.
        in_degree: dict[str, int] = {nid: 0 for nid in required}
        forward: dict[str, list[str]] = {nid: [] for nid in required}

        for nid in required:
            node = self._graph.nodes.get(nid)
            if node is None:
                continue
            for edge in node.prerequisite_ids:
                if edge.node_id in required:
                    forward[edge.node_id].append(nid)
                    in_degree[nid] += 1

        queue: deque[str] = deque(
            nid for nid, deg in in_degree.items() if deg == 0
        )
        result: list[str] = []
        while queue:
            nid = queue.popleft()
            result.append(nid)
            for dependent in forward[nid]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        return result
