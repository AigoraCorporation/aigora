import pytest

from aigora.curriculum_graph.application.graph_query import GraphQuery
from aigora.curriculum_graph.application.query_errors import (
    NodeNotFoundError,
    PathNotFoundError,
)
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.node import Node


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

    fractions = make_node("math.arithmetic.fractions")
    equations = make_node("math.algebra.linear-equations")
    quadratics = make_node("math.algebra.quadratic-equations")
    polynomials = make_node("math.algebra.polynomial-operations")
    geometry = make_node("math.geometry.triangles")

    graph.add_node(fractions)
    graph.add_node(equations)
    graph.add_node(quadratics)
    graph.add_node(polynomials)
    graph.add_node(geometry)

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


def test_should_return_direct_hard_prerequisites(graph: CurriculumGraph):
    query = GraphQuery(graph)

    result = query.get_prerequisites("math.algebra.linear-equations", include_soft=False)

    assert [node.id for node in result] == ["math.arithmetic.fractions"]


def test_should_return_direct_prerequisites_including_soft(graph: CurriculumGraph):
    query = GraphQuery(graph)

    result = query.get_prerequisites("math.algebra.quadratic-equations")

    assert [node.id for node in result] == [
        "math.algebra.linear-equations",
        "math.algebra.polynomial-operations",
    ]


def test_should_return_empty_prerequisites_when_node_has_none(graph: CurriculumGraph):
    query = GraphQuery(graph)

    result = query.get_prerequisites("math.arithmetic.fractions")

    assert result == []


def test_should_return_direct_dependents(graph: CurriculumGraph):
    query = GraphQuery(graph)

    result = query.get_dependents("math.algebra.linear-equations")

    assert [node.id for node in result] == ["math.algebra.quadratic-equations"]


def test_should_return_empty_dependents_when_node_has_none(graph: CurriculumGraph):
    query = GraphQuery(graph)

    result = query.get_dependents("math.geometry.triangles")

    assert result == []


def test_should_raise_error_when_prerequisites_node_is_missing(graph: CurriculumGraph):
    query = GraphQuery(graph)

    with pytest.raises(NodeNotFoundError, match="Node not found in CurriculumGraph"):
        query.get_prerequisites("math.unknown.missing-node")


def test_should_raise_error_when_dependents_node_is_missing(graph: CurriculumGraph):
    query = GraphQuery(graph)

    with pytest.raises(NodeNotFoundError, match="Node not found in CurriculumGraph"):
        query.get_dependents("math.unknown.missing-node")


def test_should_return_learning_path_between_connected_nodes(graph: CurriculumGraph):
    query = GraphQuery(graph)

    result = query.get_learning_path(
        "math.arithmetic.fractions",
        "math.algebra.quadratic-equations",
        include_soft=False,
    )

    assert [node.id for node in result] == [
        "math.arithmetic.fractions",
        "math.algebra.linear-equations",
        "math.algebra.quadratic-equations",
    ]


def test_should_return_single_node_path_when_start_equals_target(graph: CurriculumGraph):
    query = GraphQuery(graph)

    result = query.get_learning_path(
        "math.arithmetic.fractions",
        "math.arithmetic.fractions",
    )

    assert [node.id for node in result] == ["math.arithmetic.fractions"]


def test_should_raise_error_when_learning_path_start_node_is_missing(graph: CurriculumGraph):
    query = GraphQuery(graph)

    with pytest.raises(NodeNotFoundError, match="Node not found in CurriculumGraph"):
        query.get_learning_path(
            "math.unknown.start",
            "math.algebra.quadratic-equations",
        )


def test_should_raise_error_when_learning_path_target_node_is_missing(graph: CurriculumGraph):
    query = GraphQuery(graph)

    with pytest.raises(NodeNotFoundError, match="Node not found in CurriculumGraph"):
        query.get_learning_path(
            "math.arithmetic.fractions",
            "math.unknown.target",
        )


def test_should_raise_error_when_no_learning_path_exists(graph: CurriculumGraph):
    query = GraphQuery(graph)

    with pytest.raises(PathNotFoundError, match="No learning path found"):
        query.get_learning_path(
            "math.geometry.triangles",
            "math.algebra.quadratic-equations",
        )