from pathlib import Path
from typing import Optional

from ...application.queries import CurriculumGraphQueryService
from ...application.repository import CurriculumGraphRepository
from ...application.validators import ValidationReport, validate_graph
from ...domain.models import CanonicalNode, CurriculumProfile, PrerequisiteEdge
from ..loaders.yaml_loader import GraphLoadError, YAMLGraphLoader


class GraphValidationError(Exception):
    """Raised when the graph fails structural validation on load."""

    def __init__(self, report: ValidationReport) -> None:
        self.report = report
        super().__init__(f"Graph failed structural validation:\n{report}")


class FileBasedCurriculumGraphRepository(CurriculumGraphRepository):
    """
    A CurriculumGraphRepository backed by YAML files on disk.

    Loads and validates the graph at construction time. All queries operate
    on the in-memory validated graph. This is the reference implementation
    for the file-based phase of the project.

    Usage:
        repo = FileBasedCurriculumGraphRepository(Path("src/curriculum_graph/data/graph"))
        node = repo.get_node("algebra.equations.linear-one-variable")
        prereqs = repo.get_prerequisites("algebra.equations.linear-one-variable")

    Raises:
        GraphLoadError: if the directory structure or a YAML file is malformed.
        GraphValidationError: if the graph fails any structural validation rule.
    """

    def __init__(self, graph_dir: Path) -> None:
        graph = YAMLGraphLoader().load(graph_dir)
        report = validate_graph(graph)
        if report.has_errors:
            raise GraphValidationError(report)
        self._queries = CurriculumGraphQueryService(graph)

    def get_node(self, node_id: str) -> Optional[CanonicalNode]:
        return self._queries.get_node(node_id)

    def get_profile(self, profile_id: str) -> Optional[CurriculumProfile]:
        return self._queries.get_profile(profile_id)

    def get_prerequisites(self, node_id: str) -> list[PrerequisiteEdge]:
        return self._queries.get_prerequisites(node_id)

    def get_dependents(self, node_id: str) -> list[str]:
        return self._queries.get_dependents(node_id)

    def get_regression_targets(self, node_id: str) -> list[CanonicalNode]:
        return self._queries.get_regression_targets(node_id)

    def is_reachable(self, from_id: str, to_id: str) -> bool:
        return self._queries.is_reachable(from_id, to_id)

    def topological_order(self, profile_id: str) -> list[str]:
        return self._queries.topological_order(profile_id)
