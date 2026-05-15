from __future__ import annotations

from collections import deque

from aigora.curriculum_graph.application.errors.query_graph_errors import (
    NodeNotFoundError,
    PathNotFoundError,
)
from aigora.curriculum_graph.application.use_cases.query_graph.query_graph_command import (
    QueryGraphOperation,
    QueryGraphCommand,
)
from aigora.curriculum_graph.application.use_cases.query_graph.query_graph_result import (
    QueryGraphResult,
)
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.entities.node import Node
from aigora.curriculum_graph.domain.enums.enums import EdgeType


class QueryGraphUseCase:
    """Read-only application use case for CurriculumGraph traversal."""

    def execute(self, command: QueryGraphCommand) -> QueryGraphResult:
        graph = command.graph

        if command.operation is QueryGraphOperation.GET_NODE:
            if command.node_id is None:
                raise ValueError("node_id is required for GET_NODE queries.")
            return QueryGraphResult(nodes=[self._get_node(graph, command.node_id)])

        if command.operation is QueryGraphOperation.GET_PREREQUISITES:
            if command.node_id is None:
                raise ValueError("node_id is required for GET_PREREQUISITES queries.")
            return QueryGraphResult(
                nodes=self._get_prerequisites(
                    graph,
                    command.node_id,
                    include_soft=command.include_soft,
                )
            )

        if command.operation is QueryGraphOperation.GET_DEPENDENTS:
            if command.node_id is None:
                raise ValueError("node_id is required for GET_DEPENDENTS queries.")
            return QueryGraphResult(
                nodes=self._get_dependents(
                    graph,
                    command.node_id,
                    include_soft=command.include_soft,
                )
            )

        if command.operation is QueryGraphOperation.GET_LEARNING_PATH:
            if command.start_node_id is None or command.target_node_id is None:
                raise ValueError(
                    "start_node_id and target_node_id are required for GET_LEARNING_PATH queries."
                )
            return QueryGraphResult(
                nodes=self._get_learning_path(
                    graph,
                    command.start_node_id,
                    command.target_node_id,
                    include_soft=command.include_soft,
                )
            )

        raise ValueError(f"Unsupported graph query operation: {command.operation!r}")
    def _get_node(self, graph: CurriculumGraph, node_id: str) -> Node:
        self._ensure_node_exists(graph, node_id)
        return graph.get_node(node_id)

    def _get_prerequisites(
        self,
        graph: CurriculumGraph,
        node_id: str,
        *,
        include_soft: bool = True,
    ) -> list[Node]:
        self._ensure_node_exists(graph, node_id)

        allowed_types = {EdgeType.HARD_PREREQUISITE}
        if include_soft:
            allowed_types.add(EdgeType.SOFT_PREREQUISITE)

        prerequisite_ids = [
            edge.source
            for edge in graph.incoming_edges(node_id)
            if edge.type in allowed_types
        ]

        return [graph.get_node(prereq_id) for prereq_id in prerequisite_ids]

    def _get_dependents(
        self,
        graph: CurriculumGraph,
        node_id: str,
        *,
        include_soft: bool = True,
    ) -> list[Node]:
        self._ensure_node_exists(graph, node_id)

        allowed_types = {EdgeType.HARD_PREREQUISITE}
        if include_soft:
            allowed_types.add(EdgeType.SOFT_PREREQUISITE)

        dependent_ids = [
            edge.target
            for edge in graph.outgoing_edges(node_id)
            if edge.type in allowed_types
        ]

        return [graph.get_node(dependent_id) for dependent_id in dependent_ids]

    def _get_learning_path(
        self,
        graph: CurriculumGraph,
        start_node_id: str,
        target_node_id: str,
        *,
        include_soft: bool = True,
    ) -> list[Node]:
        self._ensure_node_exists(graph, start_node_id)
        self._ensure_node_exists(graph, target_node_id)

        if start_node_id == target_node_id:
            return [graph.get_node(start_node_id)]

        adjacency = self._build_adjacency(graph, include_soft=include_soft)

        queue: deque[str] = deque([start_node_id])
        parents: dict[str, str | None] = {start_node_id: None}

        while queue:
            current = queue.popleft()

            for neighbor in adjacency.get(current, []):
                if neighbor in parents:
                    continue

                parents[neighbor] = current

                if neighbor == target_node_id:
                    return self._reconstruct_path(graph, parents, target_node_id)

                queue.append(neighbor)

        raise PathNotFoundError(
            f"No learning path found from {start_node_id!r} to {target_node_id!r}."
        )

    def _build_adjacency(
        self,
        graph: CurriculumGraph,
        *,
        include_soft: bool,
    ) -> dict[str, list[str]]:
        allowed_types = {EdgeType.HARD_PREREQUISITE}
        if include_soft:
            allowed_types.add(EdgeType.SOFT_PREREQUISITE)

        adjacency: dict[str, list[str]] = {}

        for edge in graph.edges:
            if edge.type not in allowed_types:
                continue

            adjacency.setdefault(edge.source, []).append(edge.target)

        return adjacency

    def _reconstruct_path(
        self,
        graph: CurriculumGraph,
        parents: dict[str, str | None],
        target_node_id: str,
    ) -> list[Node]:
        path_ids: list[str] = []
        current: str | None = target_node_id

        while current is not None:
            path_ids.append(current)
            current = parents[current]

        path_ids.reverse()
        return [graph.get_node(node_id) for node_id in path_ids]

    def _ensure_node_exists(self, graph: CurriculumGraph, node_id: str) -> None:
        if node_id not in graph.nodes:
            raise NodeNotFoundError(f"Node not found in CurriculumGraph: {node_id!r}")

