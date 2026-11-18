from __future__ import annotations

from typing import overload

from aigora.curriculum_graph.application.errors.query_graph_errors import PathNotFoundError
from aigora.curriculum_graph.application.errors.read_graph_errors import (
    GraphNodeNotFoundError,
    GraphProfileNotFoundError,
    InvalidReadRequestError,
)
from aigora.curriculum_graph.application.services.published_graph_provider import PublishedGraphProvider
from aigora.curriculum_graph.application.use_cases.query_graph.query_graph_command import (
    QueryGraphCommand,
    QueryGraphOperation,
)
from aigora.curriculum_graph.application.use_cases.query_graph.query_graph_use_case import QueryGraphUseCase
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.entities.node import Node
from aigora.curriculum_graph.domain.enums.enums import EdgeType

from .read_graph_commands import (
    GetGraphMetadataCommand,
    GetLearningPathCommand,
    GetNodeCommand,
    GetPrerequisitesCommand,
    GetRegressionTargetsCommand,
    ListNodesCommand,
    ReadGraphCommand,
)
from .read_graph_results import (
    GetGraphMetadataResult,
    GetLearningPathResult,
    GetNodeResult,
    GetPrerequisitesResult,
    GetRegressionTargetsResult,
    ListNodesResult,
)
from .read_graph_views import (
    GraphMetadataView,
    MasteryCriterionView,
    NodeView,
    PrerequisiteKind,
    PrerequisiteView,
)

MAX_PAGE_SIZE = 1000

_PREREQUISITE_KINDS = {
    EdgeType.HARD_PREREQUISITE: PrerequisiteKind.HARD,
    EdgeType.SOFT_PREREQUISITE: PrerequisiteKind.SOFT,
}


class ReadGraphUseCase:
    """Read-only queries over the published graph snapshot (ADR-007).

    Every successful result carries the active `graph_version`. Errors are
    `ReadGraphError` subclasses; those raised after the snapshot is resolved
    carry its version.
    """

    def __init__(self, provider: PublishedGraphProvider, query: QueryGraphUseCase | None = None) -> None:
        self._provider = provider
        self._query = query or QueryGraphUseCase()

    @overload
    def execute(self, command: GetGraphMetadataCommand) -> GetGraphMetadataResult: ...
    @overload
    def execute(self, command: GetNodeCommand) -> GetNodeResult: ...
    @overload
    def execute(self, command: ListNodesCommand) -> ListNodesResult: ...
    @overload
    def execute(self, command: GetPrerequisitesCommand) -> GetPrerequisitesResult: ...
    @overload
    def execute(self, command: GetRegressionTargetsCommand) -> GetRegressionTargetsResult: ...
    @overload
    def execute(self, command: GetLearningPathCommand) -> GetLearningPathResult: ...

    def execute(self, command: ReadGraphCommand):
        graph = self._provider.snapshot(command.expected_version)
        version = str(graph.version)
        handler = {
            GetGraphMetadataCommand: self._metadata,
            GetNodeCommand: self._node,
            ListNodesCommand: self._list_nodes,
            GetPrerequisitesCommand: self._prerequisites,
            GetRegressionTargetsCommand: self._regression_targets,
            GetLearningPathCommand: self._learning_path,
        }.get(type(command))
        if handler is None:
            raise InvalidReadRequestError(f"Unsupported read command: {type(command).__name__}")
        return handler(graph, version, command)

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def _metadata(self, graph: CurriculumGraph, version: str, _: GetGraphMetadataCommand) -> GetGraphMetadataResult:
        return GetGraphMetadataResult(
            graph_version=version,
            metadata=GraphMetadataView(
                node_count=len(graph.nodes),
                edge_count=len(graph.edges),
                profile_count=len(graph.profiles),
                profile_ids=tuple(sorted(graph.profiles)),
                domains=tuple(sorted({node.domain for node in graph.nodes.values()})),
            ),
        )

    def _node(self, graph: CurriculumGraph, version: str, command: GetNodeCommand) -> GetNodeResult:
        node_id = _require_id(command.node_id, "node_id", version)
        _ensure_node(graph, node_id, version)
        result = self._query.execute(
            QueryGraphCommand(graph=graph, operation=QueryGraphOperation.GET_NODE, node_id=node_id)
        )
        return GetNodeResult(graph_version=version, node=to_node_view(result.nodes[0]))

    def _list_nodes(self, graph: CurriculumGraph, version: str, command: ListNodesCommand) -> ListNodesResult:
        if command.offset < 0:
            raise InvalidReadRequestError("offset must be non-negative.", graph_version=version)
        if command.limit <= 0 or command.limit > MAX_PAGE_SIZE:
            raise InvalidReadRequestError(
                f"limit must be between 1 and {MAX_PAGE_SIZE}.", graph_version=version
            )
        candidates = sorted(graph.nodes.values(), key=lambda node: str(node.id))
        if command.domain:
            candidates = [node for node in candidates if node.domain == command.domain]
        if command.profile_id:
            profile = graph.profiles.get(command.profile_id)
            if profile is None:
                raise GraphProfileNotFoundError(
                    f"Profile not found: {command.profile_id!r}", graph_version=version
                )
            referenced = profile.referenced_node_ids()
            candidates = [node for node in candidates if node.id in referenced]
        page = candidates[command.offset: command.offset + command.limit]
        end = command.offset + len(page)
        return ListNodesResult(
            graph_version=version,
            nodes=tuple(to_node_view(node) for node in page),
            total_size=len(candidates),
            next_offset=end if end < len(candidates) else None,
        )

    def _prerequisites(
        self, graph: CurriculumGraph, version: str, command: GetPrerequisitesCommand
    ) -> GetPrerequisitesResult:
        node_id = _require_id(command.node_id, "node_id", version)
        _ensure_node(graph, node_id, version)
        allowed = {EdgeType.HARD_PREREQUISITE}
        if command.include_soft:
            allowed.add(EdgeType.SOFT_PREREQUISITE)
        seen: set[str] = set()
        prerequisites: list[PrerequisiteView] = []
        for edge in graph.incoming_edges(node_id):
            if edge.type not in allowed or edge.source in seen:
                continue
            seen.add(edge.source)
            prerequisites.append(
                PrerequisiteView(node=to_node_view(graph.get_node(edge.source)), kind=_PREREQUISITE_KINDS[edge.type])
            )
        return GetPrerequisitesResult(graph_version=version, prerequisites=tuple(prerequisites))

    def _regression_targets(
        self, graph: CurriculumGraph, version: str, command: GetRegressionTargetsCommand
    ) -> GetRegressionTargetsResult:
        node_id = _require_id(command.node_id, "node_id", version)
        node = _ensure_node(graph, node_id, version)
        target_ids: list[str] = []
        for target_id in [*node.regression_ids, *(
            edge.target for edge in graph.outgoing_edges(node_id) if edge.type is EdgeType.REGRESSION_TARGET
        )]:
            if target_id not in target_ids and target_id in graph.nodes:
                target_ids.append(target_id)
        return GetRegressionTargetsResult(
            graph_version=version,
            targets=tuple(to_node_view(graph.get_node(target_id)) for target_id in target_ids),
        )

    def _learning_path(
        self, graph: CurriculumGraph, version: str, command: GetLearningPathCommand
    ) -> GetLearningPathResult:
        start = _require_id(command.start_node_id, "start_node_id", version)
        target = _require_id(command.target_node_id, "target_node_id", version)
        _ensure_node(graph, start, version)
        _ensure_node(graph, target, version)
        try:
            result = self._query.execute(
                QueryGraphCommand(
                    graph=graph,
                    operation=QueryGraphOperation.GET_LEARNING_PATH,
                    start_node_id=start,
                    target_node_id=target,
                    include_soft=command.include_soft,
                )
            )
        except PathNotFoundError:
            return GetLearningPathResult(graph_version=version, path_found=False, path=())
        return GetLearningPathResult(
            graph_version=version, path_found=True, path=tuple(to_node_view(node) for node in result.nodes)
        )


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _require_id(value: str | None, field: str, version: str) -> str:
    if value is None or not str(value).strip():
        raise InvalidReadRequestError(f"{field} is required.", graph_version=version)
    return str(value)


def _ensure_node(graph: CurriculumGraph, node_id: str, version: str) -> Node:
    node = graph.nodes.get(node_id)
    if node is None:
        raise GraphNodeNotFoundError(f"Node not found: {node_id!r}", graph_version=version)
    return node


def to_node_view(node: Node) -> NodeView:
    criteria = sorted(node.mastery_criteria.criteria_by_level.values(), key=lambda c: int(c.level))
    return NodeView(
        id=str(node.id),
        name=node.name,
        domain=node.domain,
        description=node.description,
        mastery_criteria=tuple(
            MasteryCriterionView(level=int(c.level), level_name=c.level.name, description=c.description)
            for c in criteria
        ),
        error_taxonomy=tuple(node.error_taxonomy),
        prerequisite_ids=tuple(str(i) for i in node.prerequisite_ids),
        regression_ids=tuple(str(i) for i in node.regression_ids),
    )
