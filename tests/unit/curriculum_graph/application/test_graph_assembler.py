import pytest

from aigora.curriculum_graph.application.assembler_errors import (
    DuplicateNodeError,
    DuplicateProfileError,
    UnresolvedNodeReferenceError,
)
from aigora.curriculum_graph.application.graph_assembler import GraphAssembler
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.node import Node


# ── Helpers ───────────────────────────────────────────────────────────────────


def make_node(node_id: str, domain: str = "arithmetic") -> Node:
    return Node(
        id=node_id,
        name=node_id.capitalize(),
        domain=domain,
        description=f"Description for {node_id}.",
        mastery_criteria=MasteryScale(
            criteria_by_level={
                MasteryLevel.RECOGNISES: MasteryCriterion(
                    level=MasteryLevel.RECOGNISES,
                    description="Recognises the concept.",
                )
            }
        ),
    )


def make_edge(source: str, target: str) -> Edge:
    return Edge(type=EdgeType.HARD_PREREQUISITE, source=source, target=target)


def make_profile(
    profile_id: str,
    required_nodes: list[str] | None = None,
    progression_path: list[str] | None = None,
) -> CurriculumProfile:
    return CurriculumProfile(
        id=profile_id,
        name=profile_id.upper(),
        required_nodes=set(required_nodes or []),
        progression_path=progression_path or [],
    )


# ── Happy-path ────────────────────────────────────────────────────────────────


def test_should_return_curriculum_graph_instance():
    assembler = GraphAssembler()
    graph = assembler.assemble(nodes=[], edges=[], profiles=[])

    assert isinstance(graph, CurriculumGraph)


def test_should_assemble_nodes_into_graph():
    assembler = GraphAssembler()
    nodes = [make_node("fractions"), make_node("equations")]

    graph = assembler.assemble(nodes=nodes, edges=[], profiles=[])

    assert "fractions" in graph.nodes
    assert "equations" in graph.nodes
    assert len(graph.nodes) == 2


def test_should_assemble_edges_into_graph():
    assembler = GraphAssembler()
    nodes = [make_node("fractions"), make_node("equations")]
    edges = [make_edge("fractions", "equations")]

    graph = assembler.assemble(nodes=nodes, edges=edges, profiles=[])

    assert len(graph.edges) == 1
    assert graph.edges[0].source == "fractions"
    assert graph.edges[0].target == "equations"


def test_should_assemble_profiles_into_graph():
    assembler = GraphAssembler()
    nodes = [make_node("fractions")]
    profiles = [make_profile("sat-math", required_nodes=["fractions"])]

    graph = assembler.assemble(nodes=nodes, edges=[], profiles=profiles)

    assert "sat-math" in graph.profiles


def test_should_assemble_graph_with_nodes_edges_and_profiles():
    assembler = GraphAssembler()
    nodes = [make_node("fractions"), make_node("equations")]
    edges = [make_edge("fractions", "equations")]
    profiles = [
        make_profile(
            "sat-math",
            required_nodes=["fractions", "equations"],
            progression_path=["fractions", "equations"],
        )
    ]

    graph = assembler.assemble(nodes=nodes, edges=edges, profiles=profiles)

    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert len(graph.profiles) == 1


def test_should_produce_deterministic_graph_for_equivalent_inputs():
    assembler = GraphAssembler()
    nodes = [make_node("fractions"), make_node("equations")]
    edges = [make_edge("fractions", "equations")]
    profiles = [make_profile("sat-math", required_nodes=["fractions"])]

    graph_a = assembler.assemble(nodes=nodes, edges=edges, profiles=profiles)
    graph_b = assembler.assemble(nodes=nodes, edges=edges, profiles=profiles)

    assert set(graph_a.nodes.keys()) == set(graph_b.nodes.keys())
    assert len(graph_a.edges) == len(graph_b.edges)
    assert set(graph_a.profiles.keys()) == set(graph_b.profiles.keys())


# ── Duplicate node ────────────────────────────────────────────────────────────


def test_should_raise_error_for_duplicate_node_ids():
    assembler = GraphAssembler()
    nodes = [make_node("fractions"), make_node("fractions")]

    with pytest.raises(DuplicateNodeError, match="fractions"):
        assembler.assemble(nodes=nodes, edges=[], profiles=[])


# ── Duplicate profile ─────────────────────────────────────────────────────────


def test_should_raise_error_for_duplicate_profile_ids():
    assembler = GraphAssembler()
    nodes = [make_node("fractions")]
    profiles = [
        make_profile("sat-math", required_nodes=["fractions"]),
        make_profile("sat-math", required_nodes=["fractions"]),
    ]

    with pytest.raises(DuplicateProfileError, match="sat-math"):
        assembler.assemble(nodes=nodes, edges=[], profiles=profiles)


# ── Unresolved edge references ────────────────────────────────────────────────


def test_should_raise_error_when_edge_source_is_not_a_known_node():
    assembler = GraphAssembler()
    nodes = [make_node("equations")]
    edges = [make_edge("fractions", "equations")]

    with pytest.raises(UnresolvedNodeReferenceError, match="fractions"):
        assembler.assemble(nodes=nodes, edges=edges, profiles=[])


def test_should_raise_error_when_edge_target_is_not_a_known_node():
    assembler = GraphAssembler()
    nodes = [make_node("fractions")]
    edges = [make_edge("fractions", "equations")]

    with pytest.raises(UnresolvedNodeReferenceError, match="equations"):
        assembler.assemble(nodes=nodes, edges=edges, profiles=[])


# ── Unresolved profile references ─────────────────────────────────────────────


def test_should_raise_error_when_profile_required_node_is_unknown():
    assembler = GraphAssembler()
    nodes = [make_node("fractions")]
    profiles = [make_profile("sat-math", required_nodes=["unknown-node"])]

    with pytest.raises(UnresolvedNodeReferenceError, match="unknown-node"):
        assembler.assemble(nodes=nodes, edges=[], profiles=profiles)


def test_should_raise_error_when_profile_progression_path_node_is_unknown():
    assembler = GraphAssembler()
    nodes = [make_node("fractions")]
    profiles = [make_profile("sat-math", progression_path=["unknown-node"])]

    with pytest.raises(UnresolvedNodeReferenceError, match="unknown-node"):
        assembler.assemble(nodes=nodes, edges=[], profiles=profiles)
