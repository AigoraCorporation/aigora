import pytest

from aigora.curriculum_graph.application.mapping.graph_mapper import GraphMapper
from aigora.curriculum_graph.application.mapping.mapper_errors import (
    InvalidEdgePayloadError,
    InvalidGraphPayloadError,
    InvalidNodePayloadError,
    InvalidProfilePayloadError,
)
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel


def make_valid_payload():
    return {
        "nodes": [
            {
                "id": "fractions",
                "name": "Fractions",
                "domain": "arithmetic",
                "description": "Understand fraction representation and operations.",
                "mastery": {
                    "levels": [
                        {
                            "level": 1,
                            "description": "Recognises fractions in simple contexts.",
                        },
                        {
                            "level": 3,
                            "description": "Solves fraction problems independently.",
                        },
                    ]
                },
                "prerequisites": [],
                "regressions": [],
            }
        ],
        "edges": [
            {
                "type": "hard_prerequisite",
                "source": "fractions",
                "target": "equations",
            }
        ],
        "profiles": [
            {
                "id": "sat-math",
                "name": "SAT Math",
                "required_nodes": ["fractions"],
                "mastery_targets": {"fractions": 3},
                "node_weights": {"fractions": 1.0},
                "progression_path": ["fractions"],
            }
        ],
    }


def test_should_map_valid_graph_payload_to_curriculum_graph():
    mapper = GraphMapper()
    payload = make_valid_payload()

    graph = mapper.map_graph(payload)

    assert isinstance(graph, CurriculumGraph)
    assert "fractions" in graph.nodes
    assert len(graph.edges) == 1
    assert "sat-math" in graph.profiles


def test_should_raise_error_when_graph_payload_is_not_dict():
    mapper = GraphMapper()

    with pytest.raises(InvalidGraphPayloadError, match="Graph payload must be a dictionary."):
        mapper.map_graph([])


def test_should_raise_error_when_node_payload_is_missing_required_field():
    mapper = GraphMapper()

    with pytest.raises(InvalidNodePayloadError, match="Missing required node field: name"):
        mapper.map_node(
            {
                "id": "fractions",
                "domain": "arithmetic",
                "description": "desc",
                "mastery": {"levels": [{"level": 1, "description": "desc"}]},
            }
        )


def test_should_raise_error_when_edge_type_is_invalid():
    mapper = GraphMapper()

    with pytest.raises(InvalidEdgePayloadError, match="Invalid edge type: invalid_type"):
        mapper.map_edge(
            {
                "type": "invalid_type",
                "source": "fractions",
                "target": "equations",
            }
        )


def test_should_raise_error_when_profile_mastery_target_is_invalid():
    mapper = GraphMapper()

    with pytest.raises(InvalidProfilePayloadError, match="Invalid mastery target level"):
        mapper.map_profile(
            {
                "id": "sat-math",
                "name": "SAT Math",
                "mastery_targets": {"fractions": 999},
            }
        )