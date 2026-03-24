from abc import ABC, abstractmethod
from typing import Optional

from ..domain.models import CanonicalNode, CurriculumProfile, PrerequisiteEdge


class CurriculumGraphRepository(ABC):
    """
    Abstract interface for the Curriculum Graph.

    All system components that need graph data interact with this interface.
    Callers are never coupled to the underlying storage mechanism.

    Current implementation: FileBasedCurriculumGraphRepository
    Future implementations: SqlCurriculumGraphRepository, Neo4jCurriculumGraphRepository
    """

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[CanonicalNode]:
        """Return the canonical node for the given id, or None if not found."""

    @abstractmethod
    def get_profile(self, profile_id: str) -> Optional[CurriculumProfile]:
        """Return the curriculum profile for the given id, or None if not found."""

    @abstractmethod
    def get_prerequisites(self, node_id: str) -> list[PrerequisiteEdge]:
        """
        Return all direct prerequisite edges for the given node.
        Hard prerequisites are listed before soft prerequisites.
        Returns an empty list if the node does not exist.
        """

    @abstractmethod
    def get_dependents(self, node_id: str) -> list[str]:
        """
        Return the ids of all nodes that directly declare the given node
        as a prerequisite (i.e. nodes that depend on it one hop away).
        Returns an empty list if the node does not exist or has no dependents.
        """

    @abstractmethod
    def get_regression_targets(self, node_id: str) -> list[CanonicalNode]:
        """
        Return the canonical nodes the orchestrator should revisit when
        a student's mastery of the given node breaks down.
        Returns an empty list if the node does not exist or has no regression targets.
        """

    @abstractmethod
    def is_reachable(self, from_id: str, to_id: str) -> bool:
        """
        Return True if to_id is reachable from from_id by following
        prerequisite edges (i.e. to_id is a transitive prerequisite of from_id).
        """

    @abstractmethod
    def topological_order(self, profile_id: str) -> list[str]:
        """
        Return the node ids required by the profile in a valid topological order —
        prerequisites always appear before the nodes that depend on them.
        Raises ValueError if the profile is not found.
        """
