"""Integration tests for the file-based Curriculum Graph loading flow.

These tests validate the complete runtime path from file input to final
in-memory graph assembly, covering file reading, parsing, payload mapping,
and graph assembly in sequence.

No external infrastructure is required. All tests rely on the canonical
example fixtures shipped with the repository.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from aigora.curriculum_graph.application.graph_mapper import GraphMapper
from aigora.curriculum_graph.application.graph_parser import GraphParser
from aigora.curriculum_graph.application.parser_errors import GraphStructureError
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel

_EXAMPLES_DIR = Path(__file__).parents[3] / "examples" / "curriculum_graph"


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def parser() -> GraphParser:
    return GraphParser()


@pytest.fixture(scope="module")
def mapper() -> GraphMapper:
    return GraphMapper()


@pytest.fixture(scope="module")
def canonical_yaml_graph(parser: GraphParser, mapper: GraphMapper) -> CurriculumGraph:
    path = _EXAMPLES_DIR / "canonical" / "graph.yaml"
    return mapper.map_graph(parser.parse_file(path))


@pytest.fixture(scope="module")
def canonical_json_graph(parser: GraphParser, mapper: GraphMapper) -> CurriculumGraph:
    path = _EXAMPLES_DIR / "canonical" / "graph.json"
    return mapper.map_graph(parser.parse_file(path))


# ── Full pipeline ─────────────────────────────────────────────────────────────


def test_should_load_canonical_yaml_file_to_assembled_graph(canonical_yaml_graph: CurriculumGraph):
    assert isinstance(canonical_yaml_graph, CurriculumGraph)
    assert len(canonical_yaml_graph.nodes) == 2
    assert len(canonical_yaml_graph.edges) == 1
    assert len(canonical_yaml_graph.profiles) == 1


def test_should_load_canonical_json_file_to_assembled_graph(canonical_json_graph: CurriculumGraph):
    assert isinstance(canonical_json_graph, CurriculumGraph)
    assert len(canonical_json_graph.nodes) == 2
    assert len(canonical_json_graph.edges) == 1
    assert len(canonical_json_graph.profiles) == 1


def test_yaml_and_json_canonical_files_produce_structurally_equivalent_graphs(
    canonical_yaml_graph: CurriculumGraph, canonical_json_graph: CurriculumGraph
):
    assert set(canonical_yaml_graph.nodes.keys()) == set(canonical_json_graph.nodes.keys())
    assert len(canonical_yaml_graph.edges) == len(canonical_json_graph.edges)
    assert set(canonical_yaml_graph.profiles.keys()) == set(canonical_json_graph.profiles.keys())


# ── Node assembly ─────────────────────────────────────────────────────────────


def test_should_assemble_nodes_with_correct_ids(canonical_yaml_graph: CurriculumGraph):
    assert "fractions" in canonical_yaml_graph.nodes
    assert "equations" in canonical_yaml_graph.nodes


def test_should_assemble_node_with_correct_fields(canonical_yaml_graph: CurriculumGraph):
    node = canonical_yaml_graph.nodes["fractions"]

    assert node.name == "Fractions"
    assert node.domain == "arithmetic"
    assert "fraction" in node.description.lower()


def test_should_assemble_node_with_correct_mastery_criteria(canonical_yaml_graph: CurriculumGraph):
    node = canonical_yaml_graph.nodes["fractions"]

    assert node.mastery_criteria.has_level(MasteryLevel.RECOGNISES)
    assert node.mastery_criteria.has_level(MasteryLevel.INDEPENDENT)

    criterion = node.mastery_criteria.get(MasteryLevel.RECOGNISES)
    assert criterion.description == "Recognises fractions in simple contexts."


def test_should_assemble_node_with_correct_prerequisite_ids(canonical_yaml_graph: CurriculumGraph):
    equations = canonical_yaml_graph.nodes["equations"]

    assert "fractions" in equations.prerequisite_ids


# ── Edge assembly ─────────────────────────────────────────────────────────────


def test_should_assemble_edge_with_correct_type_and_endpoints(canonical_yaml_graph: CurriculumGraph):
    edge = canonical_yaml_graph.edges[0]

    assert edge.type == EdgeType.HARD_PREREQUISITE
    assert edge.source == "fractions"
    assert edge.target == "equations"


def test_should_resolve_outgoing_edges_from_assembled_graph(canonical_yaml_graph: CurriculumGraph):
    outgoing = canonical_yaml_graph.outgoing_edges("fractions")

    assert len(outgoing) == 1
    assert outgoing[0].target == "equations"


def test_should_resolve_incoming_edges_from_assembled_graph(canonical_yaml_graph: CurriculumGraph):
    incoming = canonical_yaml_graph.incoming_edges("equations")

    assert len(incoming) == 1
    assert incoming[0].source == "fractions"


# ── Profile assembly ──────────────────────────────────────────────────────────


def test_should_assemble_profile_with_correct_id_and_name(canonical_yaml_graph: CurriculumGraph):
    assert "sat-math" in canonical_yaml_graph.profiles

    profile = canonical_yaml_graph.profiles["sat-math"]
    assert profile.name == "SAT Math"


def test_should_assemble_profile_with_correct_required_nodes(canonical_yaml_graph: CurriculumGraph):
    profile = canonical_yaml_graph.profiles["sat-math"]

    assert "fractions" in profile.required_nodes
    assert "equations" in profile.required_nodes


def test_should_assemble_profile_with_correct_mastery_targets(canonical_yaml_graph: CurriculumGraph):
    profile = canonical_yaml_graph.profiles["sat-math"]

    assert profile.mastery_targets["fractions"] == MasteryLevel.INDEPENDENT
    assert profile.mastery_targets["equations"] == MasteryLevel.EFFICIENT


def test_should_assemble_profile_with_correct_node_weights(canonical_yaml_graph: CurriculumGraph):
    profile = canonical_yaml_graph.profiles["sat-math"]

    assert profile.node_weights["fractions"] == pytest.approx(1.0)
    assert profile.node_weights["equations"] == pytest.approx(2.0)


def test_should_assemble_profile_with_correct_progression_path(canonical_yaml_graph: CurriculumGraph):
    profile = canonical_yaml_graph.profiles["sat-math"]

    assert profile.progression_path == ["fractions", "equations"]


# ── Error paths ───────────────────────────────────────────────────────────────


def test_should_raise_structure_error_for_file_with_missing_nodes_key(parser: GraphParser):
    path = _EXAMPLES_DIR / "invalid" / "missing_nodes.json"

    with pytest.raises(GraphStructureError):
        parser.parse_file(path)
