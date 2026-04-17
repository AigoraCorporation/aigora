import pytest

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
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
        name=node_id.title(),
        domain="math",
        description=f"{node_id} description",
        mastery_criteria=make_mastery_scale(),
    )


def test_should_add_node_to_graph():
    graph = CurriculumGraph()
    node = make_node("fractions")

    graph.add_node(node)

    assert graph.nodes["fractions"] == node


def test_should_raise_error_when_adding_duplicate_node():
    graph = CurriculumGraph()
    node = make_node("fractions")

    graph.add_node(node)

    with pytest.raises(ValueError, match="Duplicate node id: fractions"):
        graph.add_node(node)


def test_should_add_profile_to_graph():
    graph = CurriculumGraph()
    profile = CurriculumProfile(
        id="sat-math",
        name="SAT Math",
    )

    graph.add_profile(profile)

    assert graph.profiles["sat-math"] == profile


def test_should_raise_error_when_adding_duplicate_profile():
    graph = CurriculumGraph()
    profile = CurriculumProfile(
        id="sat-math",
        name="SAT Math",
    )

    graph.add_profile(profile)

    with pytest.raises(ValueError, match="Duplicate profile id: sat-math"):
        graph.add_profile(profile)


def test_should_add_edge_to_graph():
    graph = CurriculumGraph()
    edge = Edge(
        type=EdgeType.HARD_PREREQUISITE,
        source="fractions",
        target="equations",
    )

    graph.add_edge(edge)

    assert edge in graph.edges


def test_should_return_node_by_id():
    graph = CurriculumGraph()
    node = make_node("fractions")
    graph.add_node(node)

    result = graph.get_node("fractions")

    assert result == node


def test_should_raise_error_when_node_is_not_found():
    graph = CurriculumGraph()

    with pytest.raises(KeyError, match="Node not found: fractions"):
        graph.get_node("fractions")


def test_should_return_profile_by_id():
    graph = CurriculumGraph()
    profile = CurriculumProfile(
        id="sat-math",
        name="SAT Math",
    )
    graph.add_profile(profile)

    result = graph.get_profile("sat-math")

    assert result == profile


def test_should_raise_error_when_profile_is_not_found():
    graph = CurriculumGraph()

    with pytest.raises(KeyError, match="Profile not found: sat-math"):
        graph.get_profile("sat-math")


def test_should_return_outgoing_edges_for_node():
    graph = CurriculumGraph()
    edge_1 = Edge(
        type=EdgeType.HARD_PREREQUISITE,
        source="fractions",
        target="equations",
    )
    edge_2 = Edge(
        type=EdgeType.SOFT_PREREQUISITE,
        source="fractions",
        target="geometry",
    )
    edge_3 = Edge(
        type=EdgeType.SOFT_PREREQUISITE,
        source="algebra",
        target="geometry",
    )

    graph.add_edge(edge_1)
    graph.add_edge(edge_2)
    graph.add_edge(edge_3)

    result = graph.outgoing_edges("fractions")

    assert result == [edge_1, edge_2]


def test_should_return_incoming_edges_for_node():
    graph = CurriculumGraph()
    edge_1 = Edge(
        type=EdgeType.HARD_PREREQUISITE,
        source="fractions",
        target="equations",
    )
    edge_2 = Edge(
        type=EdgeType.SOFT_PREREQUISITE,
        source="algebra",
        target="equations",
    )
    edge_3 = Edge(
        type=EdgeType.SOFT_PREREQUISITE,
        source="algebra",
        target="geometry",
    )

    graph.add_edge(edge_1)
    graph.add_edge(edge_2)
    graph.add_edge(edge_3)

    result = graph.incoming_edges("equations")

    assert result == [edge_1, edge_2]


def test_should_return_edges_filtered_by_type():
    graph = CurriculumGraph()
    edge_1 = Edge(
        type=EdgeType.HARD_PREREQUISITE,
        source="fractions",
        target="equations",
    )
    edge_2 = Edge(
        type=EdgeType.SOFT_PREREQUISITE,
        source="algebra",
        target="equations",
    )

    graph.add_edge(edge_1)
    graph.add_edge(edge_2)

    result = graph.edges_by_type(EdgeType.HARD_PREREQUISITE)

    assert result == [edge_1]