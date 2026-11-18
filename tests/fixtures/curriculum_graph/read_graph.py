"""Shared fixtures for read-only graph access tests (ADR-007).

Graph (version "2026.11.0"):

    a.counting --hard--> a.fractions --hard--> b.linear-equations --soft--> b.quadratics
                         a.decimals   --soft--> b.linear-equations
    b.quadratics --regression_target--> a.fractions   (+ declared regression_ids: b.linear-equations)
    c.isolated (no edges)

Profile "profile.core" references a.counting, a.fractions, b.linear-equations.
"""
from __future__ import annotations

from aigora.curriculum_graph.application.ports.curriculum_graph_reader import CurriculumGraphReader
from aigora.curriculum_graph.application.errors.read_graph_errors import GraphUnavailableError
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.entities.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.entities.edge import Edge
from aigora.curriculum_graph.domain.entities.node import Node
from aigora.curriculum_graph.domain.enums.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.value_objects.mastery import MasteryCriterion, MasteryScale

GRAPH_VERSION = "2026.11.0"


def make_node(node_id: str, domain: str, *, regression_ids: list[str] | None = None) -> Node:
    return Node(
        id=node_id,
        name=node_id.split(".")[-1].replace("-", " ").title(),
        domain=domain,
        description=f"{node_id} description",
        mastery_criteria=MasteryScale(
            criteria_by_level={
                MasteryLevel.INDEPENDENT: MasteryCriterion(MasteryLevel.INDEPENDENT, "Solves independently."),
                MasteryLevel.RECOGNISES: MasteryCriterion(MasteryLevel.RECOGNISES, "Recognises the concept."),
            }
        ),
        error_taxonomy=[f"{node_id}.misconception"],
        regression_ids=regression_ids or [],
    )


def make_graph(version: str | None = GRAPH_VERSION) -> CurriculumGraph:
    graph = CurriculumGraph(version=version)
    for node in [
        make_node("a.counting", "arithmetic"),
        make_node("a.decimals", "arithmetic"),
        make_node("a.fractions", "arithmetic"),
        make_node("b.linear-equations", "algebra"),
        make_node("b.quadratics", "algebra", regression_ids=["b.linear-equations"]),
        make_node("c.isolated", "geometry"),
    ]:
        graph.add_node(node)
    for edge_type, source, target in [
        (EdgeType.HARD_PREREQUISITE, "a.counting", "a.fractions"),
        (EdgeType.HARD_PREREQUISITE, "a.fractions", "b.linear-equations"),
        (EdgeType.SOFT_PREREQUISITE, "a.decimals", "b.linear-equations"),
        (EdgeType.SOFT_PREREQUISITE, "b.linear-equations", "b.quadratics"),
        (EdgeType.REGRESSION_TARGET, "b.quadratics", "a.fractions"),
    ]:
        graph.add_edge(Edge(type=edge_type, source=source, target=target))
    graph.add_profile(
        CurriculumProfile(
            id="profile.core",
            name="Core",
            required_nodes={"a.counting", "a.fractions"},
            mastery_targets={"b.linear-equations": MasteryLevel.GUIDED},
            node_weights={"a.fractions": 2.0},
            progression_path=["a.counting", "a.fractions", "b.linear-equations"],
            exam_skill_overlay=["fuvest"],
        )
    )
    return graph


class StaticGraphReader(CurriculumGraphReader):
    """Reader double returning a fixed graph, or failing with GraphUnavailableError."""

    def __init__(self, graph: CurriculumGraph | None = None, *, fail: bool = False) -> None:
        self.graph = graph if graph is not None else make_graph()
        self.fail = fail
        self.calls = 0

    def load_published(self) -> CurriculumGraph:
        self.calls += 1
        if self.fail:
            raise GraphUnavailableError("The graph store is unreachable.")
        return self.graph
