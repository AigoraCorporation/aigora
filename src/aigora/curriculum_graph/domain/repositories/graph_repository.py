from __future__ import annotations

from typing import Protocol

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph


class GraphRepository(Protocol):
    """Port defining the persistence contract for CurriculumGraph.

    Implementations must reside in the infrastructure layer.
    No Neo4j driver types or infrastructure-specific imports are
    permitted in this interface.
    """

    def apply_schema(self) -> None:
        """Apply the required database schema (constraints and indexes).

        Must be idempotent — safe to call multiple times.
        """
        ...

    def persist(self, graph: CurriculumGraph) -> None:
        """Persist the given CurriculumGraph.

        Must be idempotent — repeated calls with the same graph must
        not create duplicate nodes, edges, or profiles.
        """
        ...

    def validate(self, graph: CurriculumGraph) -> None:
        """Run post-persistence validation against the stored graph.

        Raises an exception if the persisted state does not minimally
        reflect the provided in-memory graph.
        """
        ...
