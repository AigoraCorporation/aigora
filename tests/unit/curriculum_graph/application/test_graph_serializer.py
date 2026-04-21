import json

import pytest
import yaml

from aigora.curriculum_graph.application.graph_serializer import GraphSerializer
from aigora.curriculum_graph.application.serializer_errors import (
    UnsupportedSerializationFormatError,
)
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.node import Node


# ── Helpers ───────────────────────────────────────────────────────────────────


def make_mastery_scale(*levels: MasteryLevel) -> MasteryScale:
    return MasteryScale(
        criteria_by_level={
            level: MasteryCriterion(
                level=level,
                description=f"Description for {level.name}.",
            )
            for level in levels
        }
    )


def make_node(node_id: str) -> Node:
    return Node(
        id=node_id,
        name=node_id.split(".")[-1].replace("-", " ").title(),
        domain="mathematics",
        description=f"Description for {node_id}.",
        mastery_criteria=make_mastery_scale(MasteryLevel.RECOGNISES, MasteryLevel.INDEPENDENT),
    )


def make_edge(source: str, target: str) -> Edge:
    return Edge(type=EdgeType.HARD_PREREQUISITE, source=source, target=target)


def make_profile(profile_id: str, required_nodes: list[str]) -> CurriculumProfile:
    return CurriculumProfile(
        id=profile_id,
        name="Test Profile",
        required_nodes=set(required_nodes),
        mastery_targets={n: MasteryLevel.INDEPENDENT for n in required_nodes},
        node_weights={n: 1.0 for n in required_nodes},
        progression_path=required_nodes,
    )


def make_full_graph() -> CurriculumGraph:
    graph = CurriculumGraph()
    node_a = make_node("math.arithmetic.fractions")
    node_b = make_node("math.algebra.linear-equations")
    graph.add_node(node_a)
    graph.add_node(node_b)
    graph.add_edge(make_edge("math.arithmetic.fractions", "math.algebra.linear-equations"))
    graph.add_profile(
        make_profile(
            "profile.sat-math",
            ["math.arithmetic.fractions", "math.algebra.linear-equations"],
        )
    )
    return graph


# ── Happy path ────────────────────────────────────────────────────────────────


def test_should_serialize_graph_to_dict():
    serializer = GraphSerializer()
    graph = make_full_graph()

    result = serializer.to_dict(graph)

    assert "nodes" in result
    assert "edges" in result
    assert "profiles" in result
    assert len(result["nodes"]) == 2
    assert len(result["edges"]) == 1
    assert len(result["profiles"]) == 1


def test_should_include_all_node_fields_in_dict():
    serializer = GraphSerializer()
    graph = CurriculumGraph()
    graph.add_node(make_node("math.arithmetic.fractions"))

    result = serializer.to_dict(graph)
    node = result["nodes"][0]

    assert node["id"] == "math.arithmetic.fractions"
    assert node["name"] == "Fractions"
    assert node["domain"] == "mathematics"
    assert "description" in node
    assert "mastery" in node
    assert "prerequisites" in node
    assert "regressions" in node


def test_should_include_mastery_levels_in_node_serialization():
    serializer = GraphSerializer()
    graph = CurriculumGraph()
    graph.add_node(make_node("math.arithmetic.fractions"))

    result = serializer.to_dict(graph)
    mastery = result["nodes"][0]["mastery"]

    assert "levels" in mastery
    assert len(mastery["levels"]) == 2
    level_values = {entry["level"] for entry in mastery["levels"]}
    assert MasteryLevel.RECOGNISES.value in level_values
    assert MasteryLevel.INDEPENDENT.value in level_values


def test_should_include_all_edge_fields_in_dict():
    serializer = GraphSerializer()
    graph = CurriculumGraph()
    graph.add_edge(make_edge("math.arithmetic.fractions", "math.algebra.linear-equations"))

    result = serializer.to_dict(graph)
    edge = result["edges"][0]

    assert edge["type"] == "hard_prerequisite"
    assert edge["source"] == "math.arithmetic.fractions"
    assert edge["target"] == "math.algebra.linear-equations"


def test_should_include_all_profile_fields_in_dict():
    serializer = GraphSerializer()
    graph = CurriculumGraph()
    graph.add_profile(
        make_profile("profile.sat-math", ["math.arithmetic.fractions"])
    )

    result = serializer.to_dict(graph)
    profile = result["profiles"][0]

    assert profile["id"] == "profile.sat-math"
    assert profile["name"] == "Test Profile"
    assert "required_nodes" in profile
    assert "mastery_targets" in profile
    assert "node_weights" in profile
    assert "progression_path" in profile


def test_should_serialize_graph_to_valid_json():
    serializer = GraphSerializer()
    graph = make_full_graph()

    result = serializer.to_json(graph)
    parsed = json.loads(result)

    assert "nodes" in parsed
    assert "edges" in parsed
    assert "profiles" in parsed


def test_should_serialize_graph_to_valid_yaml():
    serializer = GraphSerializer()
    graph = make_full_graph()

    result = serializer.to_yaml(graph)
    parsed = yaml.safe_load(result)

    assert "nodes" in parsed
    assert "edges" in parsed
    assert "profiles" in parsed


def test_should_serialize_via_format_dispatch_json():
    serializer = GraphSerializer()
    graph = make_full_graph()

    result = serializer.serialize(graph, "json")
    parsed = json.loads(result)

    assert "nodes" in parsed


def test_should_serialize_via_format_dispatch_yaml():
    serializer = GraphSerializer()
    graph = make_full_graph()

    result = serializer.serialize(graph, "yaml")
    parsed = yaml.safe_load(result)

    assert "nodes" in parsed


# ── Edge cases ────────────────────────────────────────────────────────────────


def test_should_serialize_graph_with_empty_edges():
    serializer = GraphSerializer()
    graph = CurriculumGraph()
    graph.add_node(make_node("math.arithmetic.fractions"))

    result = serializer.to_dict(graph)

    assert result["edges"] == []


def test_should_serialize_graph_with_empty_profiles():
    serializer = GraphSerializer()
    graph = CurriculumGraph()
    graph.add_node(make_node("math.arithmetic.fractions"))

    result = serializer.to_dict(graph)

    assert result["profiles"] == []


def test_should_serialize_empty_graph():
    serializer = GraphSerializer()
    graph = CurriculumGraph()

    result = serializer.to_dict(graph)

    assert result["nodes"] == []
    assert result["edges"] == []
    assert result["profiles"] == []


def test_should_produce_valid_json_for_empty_graph():
    serializer = GraphSerializer()
    graph = CurriculumGraph()

    result = serializer.to_json(graph)
    parsed = json.loads(result)

    assert parsed == {"nodes": [], "edges": [], "profiles": []}


def test_should_produce_valid_yaml_for_empty_graph():
    serializer = GraphSerializer()
    graph = CurriculumGraph()

    result = serializer.to_yaml(graph)
    parsed = yaml.safe_load(result)

    assert parsed["nodes"] == []
    assert parsed["edges"] == []
    assert parsed["profiles"] == []


# ── Failure cases ─────────────────────────────────────────────────────────────


def test_should_raise_error_for_unsupported_format():
    serializer = GraphSerializer()
    graph = CurriculumGraph()

    with pytest.raises(UnsupportedSerializationFormatError, match="Unsupported serialization format"):
        serializer.serialize(graph, "xml")


def test_should_raise_error_for_empty_format_string():
    serializer = GraphSerializer()
    graph = CurriculumGraph()

    with pytest.raises(UnsupportedSerializationFormatError):
        serializer.serialize(graph, "")


def test_should_raise_error_for_unknown_format():
    serializer = GraphSerializer()
    graph = CurriculumGraph()

    with pytest.raises(UnsupportedSerializationFormatError):
        serializer.serialize(graph, "csv")
