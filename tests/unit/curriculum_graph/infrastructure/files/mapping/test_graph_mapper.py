import pytest

from aigora.curriculum_graph.infrastructure.files.mapping.curriculum_graph_mapper import CurriculumGraphMapper
from aigora.curriculum_graph.infrastructure.files.errors.mapper_errors import (
    InvalidEdgePayloadError,
    InvalidGraphPayloadError,
    InvalidNodePayloadError,
    InvalidProfilePayloadError,
)
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.enums.enums import EdgeType, MasteryLevel


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
    mapper = CurriculumGraphMapper()
    payload = make_valid_payload()

    graph = mapper.map_graph(payload)

    assert isinstance(graph, CurriculumGraph)
    assert "fractions" in graph.nodes
    assert len(graph.edges) == 1
    assert "sat-math" in graph.profiles


def test_should_raise_error_when_graph_payload_is_not_dict():
    mapper = CurriculumGraphMapper()

    with pytest.raises(InvalidGraphPayloadError, match="Graph payload must be a dictionary."):
        mapper.map_graph([])


def test_should_raise_error_when_node_payload_is_missing_required_field():
    mapper = CurriculumGraphMapper()

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
    mapper = CurriculumGraphMapper()

    with pytest.raises(InvalidEdgePayloadError, match="Invalid edge type: invalid_type"):
        mapper.map_edge(
            {
                "type": "invalid_type",
                "source": "fractions",
                "target": "equations",
            }
        )


def test_should_raise_error_when_profile_mastery_target_is_invalid():
    mapper = CurriculumGraphMapper()

    with pytest.raises(InvalidProfilePayloadError, match="Invalid mastery target level"):
        mapper.map_profile(
            {
                "id": "sat-math",
                "name": "SAT Math",
                "mastery_targets": {"fractions": 999},
            }
        )

@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"edges": []}, "nodes.*list"),
        ({"nodes": [], "edges": "invalid"}, "edges.*list"),
        ({"nodes": [], "edges": [], "profiles": "invalid"}, "profiles.*list"),
        ({"version": 123, "nodes": [], "edges": []}, "version.*string"),
    ],
)
def test_should_validate_graph_collection_fields(payload, message):
    with pytest.raises(InvalidGraphPayloadError, match=message):
        CurriculumGraphMapper().map_graph(payload)


@pytest.mark.parametrize(
    ("payload", "expected_error", "message"),
    [
        ([], InvalidNodePayloadError, "Node payload must be a dictionary"),
        ({}, InvalidNodePayloadError, "mastery.*dictionary"),
        ({"mastery": {}}, InvalidNodePayloadError, "levels.*list"),
        ({"mastery": {"levels": ["invalid"]}}, InvalidNodePayloadError, "level entry.*dictionary"),
        ({"mastery": {"levels": [{}]}}, InvalidNodePayloadError, "contain 'level'"),
        ({"mastery": {"levels": [{"level": 999}]}}, InvalidNodePayloadError, "Invalid mastery level"),
        ({"mastery": {"levels": [{"level": 1}]}}, InvalidNodePayloadError, "contain 'description'"),
    ],
)
def test_should_validate_node_payload_shapes(payload, expected_error, message):
    with pytest.raises(expected_error, match=message):
        CurriculumGraphMapper().map_node(payload)


def test_should_wrap_node_value_errors_as_node_payload_errors():
    with pytest.raises(InvalidNodePayloadError, match="Node id must be non-empty"):
        CurriculumGraphMapper().map_node(
            {
                "id": " ",
                "name": "Fractions",
                "domain": "arithmetic",
                "description": "desc",
                "mastery": {"levels": [{"level": 1, "description": "desc"}]},
            }
        )


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "Edge payload must be a dictionary"),
        ({}, "Missing required edge field: type"),
        ({"type": "hard_prerequisite"}, "Missing required edge field: source"),
        ({"type": "hard_prerequisite", "source": "a"}, "Missing required edge field: target"),
    ],
)
def test_should_validate_edge_payload_shapes(payload, message):
    with pytest.raises(InvalidEdgePayloadError, match=message):
        CurriculumGraphMapper().map_edge(payload)


def test_should_wrap_edge_value_errors_as_edge_payload_errors():
    with pytest.raises(InvalidEdgePayloadError, match="source must be non-empty"):
        CurriculumGraphMapper().map_edge(
            {
                "type": "hard_prerequisite",
                "source": " ",
                "target": "equations",
            }
        )


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ([], "Profile payload must be a dictionary"),
        ({"id": "sat", "name": "SAT", "mastery_targets": []}, "mastery_targets.*dictionary"),
        ({"name": "SAT"}, "Missing required profile field: id"),
        ({"id": "sat"}, "Missing required profile field: name"),
    ],
)
def test_should_validate_profile_payload_shapes(payload, message):
    with pytest.raises(InvalidProfilePayloadError, match=message):
        CurriculumGraphMapper().map_profile(payload)


def test_should_wrap_profile_value_errors_as_profile_payload_errors():
    with pytest.raises(InvalidProfilePayloadError, match="CurriculumProfile id must be non-empty"):
        CurriculumGraphMapper().map_profile({"id": " ", "name": "SAT Math"})
