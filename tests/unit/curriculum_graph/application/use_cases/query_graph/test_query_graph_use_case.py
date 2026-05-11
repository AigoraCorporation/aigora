import pytest

from aigora.curriculum_graph.application.errors.query_graph_errors import (
    NodeNotFoundError,
    PathNotFoundError,
)
from aigora.curriculum_graph.application.use_cases.query_graph.query_graph_command import (
    QueryGraphOperation,
    QueryGraphCommand,
)
from aigora.curriculum_graph.application.use_cases.query_graph.query_graph_use_case import (
    QueryGraphUseCase,
)
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.entities.edge import Edge
from aigora.curriculum_graph.domain.entities.node import Node
from aigora.curriculum_graph.domain.enums.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.value_objects.mastery import MasteryCriterion, MasteryScale


def make_mastery_scale() -> MasteryScale:
    return MasteryScale(
        criteria_by_level={
            MasteryLevel.RECOGNISES: MasteryCriterion(
                level=MasteryLevel.RECOGNISES,
                description="Recognises the concept.",
            )
        }
    )


def make_node(node_id: str) -> Node:
    return Node(
        id=node_id,
        name=node_id.split(".")[-1].replace("-", " ").title(),
        domain="mathematics",
        description=f"{node_id} description",
        mastery_criteria=make_mastery_scale(),
    )


def make_edge(
    source: str,
    target: str,
    edge_type: EdgeType = EdgeType.HARD_PREREQUISITE,
) -> Edge:
    return Edge(
        type=edge_type,
        source=source,
        target=target,
    )


@pytest.fixture
def graph() -> CurriculumGraph:
    graph = CurriculumGraph()

    for node_id in (
        "math.arithmetic.fractions",
        "math.algebra.linear-equations",
        "math.algebra.quadratic-equations",
        "math.algebra.polynomial-operations",
        "math.geometry.triangles",
    ):
        graph.add_node(make_node(node_id))

    graph.add_edge(
        make_edge(
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
            EdgeType.HARD_PREREQUISITE,
        )
    )
    graph.add_edge(
        make_edge(
            "math.algebra.linear-equations",
            "math.algebra.quadratic-equations",
            EdgeType.HARD_PREREQUISITE,
        )
    )
    graph.add_edge(
        make_edge(
            "math.algebra.polynomial-operations",
            "math.algebra.quadratic-equations",
            EdgeType.SOFT_PREREQUISITE,
        )
    )

    return graph


def execute_query(graph: CurriculumGraph, **kwargs):
    return QueryGraphUseCase().execute(QueryGraphCommand(graph=graph, **kwargs)).nodes


def test_should_return_node_by_id(graph: CurriculumGraph):
    result = execute_query(
        graph,
        operation=QueryGraphOperation.GET_NODE,
        node_id="math.arithmetic.fractions",
    )

    assert [node.id for node in result] == ["math.arithmetic.fractions"]


def test_should_raise_error_when_node_is_missing(graph: CurriculumGraph):
    with pytest.raises(NodeNotFoundError, match="Node not found in CurriculumGraph"):
        execute_query(
            graph,
            operation=QueryGraphOperation.GET_NODE,
            node_id="math.unknown.missing-node",
        )


def test_should_return_direct_hard_prerequisites(graph: CurriculumGraph):
    result = execute_query(
        graph,
        operation=QueryGraphOperation.GET_PREREQUISITES,
        node_id="math.algebra.linear-equations",
        include_soft=False,
    )

    assert [node.id for node in result] == ["math.arithmetic.fractions"]


def test_should_return_direct_prerequisites_including_soft(graph: CurriculumGraph):
    result = execute_query(
        graph,
        operation=QueryGraphOperation.GET_PREREQUISITES,
        node_id="math.algebra.quadratic-equations",
    )

    assert [node.id for node in result] == [
        "math.algebra.linear-equations",
        "math.algebra.polynomial-operations",
    ]


def test_should_return_empty_prerequisites_when_node_has_none(graph: CurriculumGraph):
    result = execute_query(
        graph,
        operation=QueryGraphOperation.GET_PREREQUISITES,
        node_id="math.arithmetic.fractions",
    )

    assert result == []


def test_should_return_direct_dependents(graph: CurriculumGraph):
    result = execute_query(
        graph,
        operation=QueryGraphOperation.GET_DEPENDENTS,
        node_id="math.algebra.linear-equations",
    )

    assert [node.id for node in result] == ["math.algebra.quadratic-equations"]


def test_should_return_empty_dependents_when_node_has_none(graph: CurriculumGraph):
    result = execute_query(
        graph,
        operation=QueryGraphOperation.GET_DEPENDENTS,
        node_id="math.geometry.triangles",
    )

    assert result == []


def test_should_raise_error_when_prerequisites_node_is_missing(graph: CurriculumGraph):
    with pytest.raises(NodeNotFoundError, match="Node not found in CurriculumGraph"):
        execute_query(
            graph,
            operation=QueryGraphOperation.GET_PREREQUISITES,
            node_id="math.unknown.missing-node",
        )


def test_should_raise_error_when_dependents_node_is_missing(graph: CurriculumGraph):
    with pytest.raises(NodeNotFoundError, match="Node not found in CurriculumGraph"):
        execute_query(
            graph,
            operation=QueryGraphOperation.GET_DEPENDENTS,
            node_id="math.unknown.missing-node",
        )


def test_should_return_learning_path_between_connected_nodes(graph: CurriculumGraph):
    result = execute_query(
        graph,
        operation=QueryGraphOperation.GET_LEARNING_PATH,
        start_node_id="math.arithmetic.fractions",
        target_node_id="math.algebra.quadratic-equations",
        include_soft=False,
    )

    assert [node.id for node in result] == [
        "math.arithmetic.fractions",
        "math.algebra.linear-equations",
        "math.algebra.quadratic-equations",
    ]


def test_should_return_single_node_path_when_start_equals_target(graph: CurriculumGraph):
    result = execute_query(
        graph,
        operation=QueryGraphOperation.GET_LEARNING_PATH,
        start_node_id="math.arithmetic.fractions",
        target_node_id="math.arithmetic.fractions",
    )

    assert [node.id for node in result] == ["math.arithmetic.fractions"]


def test_should_raise_error_when_learning_path_start_node_is_missing(graph: CurriculumGraph):
    with pytest.raises(NodeNotFoundError, match="Node not found in CurriculumGraph"):
        execute_query(
            graph,
            operation=QueryGraphOperation.GET_LEARNING_PATH,
            start_node_id="math.unknown.start",
            target_node_id="math.algebra.quadratic-equations",
        )


def test_should_raise_error_when_learning_path_target_node_is_missing(graph: CurriculumGraph):
    with pytest.raises(NodeNotFoundError, match="Node not found in CurriculumGraph"):
        execute_query(
            graph,
            operation=QueryGraphOperation.GET_LEARNING_PATH,
            start_node_id="math.arithmetic.fractions",
            target_node_id="math.unknown.target",
        )


def test_should_raise_error_when_no_learning_path_exists(graph: CurriculumGraph):
    with pytest.raises(PathNotFoundError, match="No learning path found"):
        execute_query(
            graph,
            operation=QueryGraphOperation.GET_LEARNING_PATH,
            start_node_id="math.geometry.triangles",
            target_node_id="math.algebra.quadratic-equations",
        )


def test_should_require_node_id_for_get_node(graph: CurriculumGraph):
    with pytest.raises(ValueError, match="node_id is required for GET_NODE"):
        QueryGraphUseCase().execute(
            QueryGraphCommand(graph=graph, operation=QueryGraphOperation.GET_NODE)
        )


def test_should_require_node_id_for_get_prerequisites(graph: CurriculumGraph):
    with pytest.raises(ValueError, match="node_id is required for GET_PREREQUISITES"):
        QueryGraphUseCase().execute(
            QueryGraphCommand(graph=graph, operation=QueryGraphOperation.GET_PREREQUISITES)
        )


def test_should_require_node_id_for_get_dependents(graph: CurriculumGraph):
    with pytest.raises(ValueError, match="node_id is required for GET_DEPENDENTS"):
        QueryGraphUseCase().execute(
            QueryGraphCommand(graph=graph, operation=QueryGraphOperation.GET_DEPENDENTS)
        )


def test_should_require_start_and_target_for_learning_path(graph: CurriculumGraph):
    with pytest.raises(ValueError, match="start_node_id and target_node_id"):
        QueryGraphUseCase().execute(
            QueryGraphCommand(graph=graph, operation=QueryGraphOperation.GET_LEARNING_PATH)
        )


def test_should_reject_unsupported_operation(graph: CurriculumGraph):
    command = QueryGraphCommand(graph=graph, operation=QueryGraphOperation.GET_NODE)
    object.__setattr__(command, "operation", "invalid-operation")

    with pytest.raises(ValueError, match="Unsupported graph query operation"):
        QueryGraphUseCase().execute(command)
