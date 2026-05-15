from __future__ import annotations

from dataclasses import dataclass, field

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.infrastructure.neo4j.errors import (
    GraphPersistenceValidationError,
)


@dataclass
class PersistenceValidationResult:
    """Raw counts and IDs returned from the infrastructure layer."""

    persisted_node_count: int
    persisted_edge_count: int
    found_node_ids: set[str] = field(default_factory=set)
    found_profile_ids: set[str] = field(default_factory=set)


class CurriculumGraphPersistenceValidator:
    """Application-level orchestrator for post-persistence validation.

    Compares raw counts and IDs returned by the infrastructure layer
    against the in-memory CurriculumGraph.

    Does not contain Cypher or any database-specific logic.
    """

    def validate(
        self,
        graph: CurriculumGraph,
        result: PersistenceValidationResult,
    ) -> None:
        """Run all post-persistence checks against the given result.

        Raises:
            GraphPersistenceValidationError: On the first mismatch found.
        """
        self._check_node_count(graph, result)
        self._check_edge_count(graph, result)
        self._check_required_node_ids(graph, result)
        self._check_profile_consistency(graph, result)

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_node_count(
        self,
        graph: CurriculumGraph,
        result: PersistenceValidationResult,
    ) -> None:
        expected = len(graph.nodes)
        if result.persisted_node_count < expected:
            raise GraphPersistenceValidationError(
                f"Node count mismatch: expected {expected}, "
                f"found {result.persisted_node_count}"
            )

    def _check_edge_count(
        self,
        graph: CurriculumGraph,
        result: PersistenceValidationResult,
    ) -> None:
        expected = len(graph.edges)
        if result.persisted_edge_count < expected:
            raise GraphPersistenceValidationError(
                f"Edge count mismatch: expected {expected}, "
                f"found {result.persisted_edge_count}"
            )

    def _check_required_node_ids(
        self,
        graph: CurriculumGraph,
        result: PersistenceValidationResult,
    ) -> None:
        expected_ids = set(graph.nodes.keys())
        missing = expected_ids - result.found_node_ids
        if missing:
            raise GraphPersistenceValidationError(
                f"Missing persisted node IDs: {missing}"
            )

    def _check_profile_consistency(
        self,
        graph: CurriculumGraph,
        result: PersistenceValidationResult,
    ) -> None:
        expected_ids = set(graph.profiles.keys())
        if not expected_ids:
            return
        missing = expected_ids - result.found_profile_ids
        if missing:
            raise GraphPersistenceValidationError(
                f"Missing persisted profile IDs: {missing}"
            )
