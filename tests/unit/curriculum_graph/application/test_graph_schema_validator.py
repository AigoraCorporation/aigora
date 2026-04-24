import pytest

from aigora.curriculum_graph.application.graph_schema_validator import GraphSchemaValidator
from aigora.curriculum_graph.application.schema_errors import SchemaValidationError


# ── Helpers ───────────────────────────────────────────────────────────────────


def make_valid_payload():
    return {
        "nodes": [
            {
                "id": "math.arithmetic.fractions",
                "name": "Fractions",
                "domain": "arithmetic",
                "description": "Understand fraction representation and operations.",
                "mastery": {
                    "levels": [
                        {"level": 1, "description": "Recognises fractions."},
                        {"level": 3, "description": "Solves independently."},
                    ]
                },
                "prerequisites": [],
                "regressions": [],
            }
        ],
        "edges": [
            {
                "type": "hard_prerequisite",
                "source": "math.arithmetic.fractions",
                "target": "math.algebra.linear-equations",
            }
        ],
        "profiles": [
            {
                "id": "profile.sat-math",
                "name": "SAT Math",
                "required_nodes": ["math.arithmetic.fractions"],
                "mastery_targets": {"math.arithmetic.fractions": 3},
                "node_weights": {"math.arithmetic.fractions": 1.0},
                "progression_path": ["math.arithmetic.fractions"],
            }
        ],
    }


# ── Happy path ────────────────────────────────────────────────────────────────


def test_should_accept_valid_payload():
    validator = GraphSchemaValidator()
    validator.validate(make_valid_payload())


def test_should_accept_payload_without_profiles():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["profiles"]
    validator.validate(payload)


def test_should_accept_payload_with_empty_profiles():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["profiles"] = []
    validator.validate(payload)


def test_should_accept_payload_with_empty_edges():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["edges"] = []
    validator.validate(payload)


def test_should_accept_node_without_optional_list_fields():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    node = payload["nodes"][0]
    del node["prerequisites"]
    del node["regressions"]
    validator.validate(payload)


def test_should_accept_profile_without_optional_fields():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["profiles"] = [{"id": "profile.minimal", "name": "Minimal Profile"}]
    validator.validate(payload)


def test_should_accept_all_valid_edge_types():
    validator = GraphSchemaValidator()
    for edge_type in ("hard_prerequisite", "soft_prerequisite", "regression_target"):
        payload = make_valid_payload()
        payload["edges"][0]["type"] = edge_type
        validator.validate(payload)


def test_should_accept_all_valid_mastery_levels():
    validator = GraphSchemaValidator()
    for level in (0, 1, 2, 3, 4, 5):
        payload = make_valid_payload()
        payload["nodes"][0]["mastery"]["levels"][0]["level"] = level
        validator.validate(payload)


# ── Failure cases — top-level ─────────────────────────────────────────────────


def test_should_raise_error_when_payload_is_not_dict():
    validator = GraphSchemaValidator()
    with pytest.raises(SchemaValidationError, match="must be a dictionary"):
        validator.validate([])


def test_should_raise_error_when_nodes_missing():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["nodes"]
    with pytest.raises(SchemaValidationError, match="'nodes'"):
        validator.validate(payload)


def test_should_raise_error_when_edges_missing():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["edges"]
    with pytest.raises(SchemaValidationError, match="'edges'"):
        validator.validate(payload)


def test_should_raise_error_when_nodes_is_not_list():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["nodes"] = "not-a-list"
    with pytest.raises(SchemaValidationError, match="'nodes' must be a list"):
        validator.validate(payload)


def test_should_raise_error_when_edges_is_not_list():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["edges"] = {"key": "value"}
    with pytest.raises(SchemaValidationError, match="'edges' must be a list"):
        validator.validate(payload)


def test_should_raise_error_when_profiles_is_not_list():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["profiles"] = "not-a-list"
    with pytest.raises(SchemaValidationError, match="'profiles' must be a list"):
        validator.validate(payload)


# ── Failure cases — nodes ─────────────────────────────────────────────────────


def test_should_raise_error_when_node_is_not_dict():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["nodes"] = ["not-a-dict"]
    with pytest.raises(SchemaValidationError, match="Node at index 0 must be a dictionary"):
        validator.validate(payload)


def test_should_raise_error_when_node_missing_id():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["nodes"][0]["id"]
    with pytest.raises(SchemaValidationError, match="'id'"):
        validator.validate(payload)


def test_should_raise_error_when_node_missing_name():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["nodes"][0]["name"]
    with pytest.raises(SchemaValidationError, match="'name'"):
        validator.validate(payload)


def test_should_raise_error_when_node_missing_domain():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["nodes"][0]["domain"]
    with pytest.raises(SchemaValidationError, match="'domain'"):
        validator.validate(payload)


def test_should_raise_error_when_node_missing_description():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["nodes"][0]["description"]
    with pytest.raises(SchemaValidationError, match="'description'"):
        validator.validate(payload)


def test_should_raise_error_when_node_missing_mastery():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["nodes"][0]["mastery"]
    with pytest.raises(SchemaValidationError, match="'mastery'"):
        validator.validate(payload)


def test_should_raise_error_when_node_id_is_not_string():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["nodes"][0]["id"] = 42
    with pytest.raises(SchemaValidationError, match="'id' must be a string"):
        validator.validate(payload)


def test_should_raise_error_when_node_mastery_levels_missing():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["nodes"][0]["mastery"]["levels"]
    with pytest.raises(SchemaValidationError, match="'levels'"):
        validator.validate(payload)


def test_should_raise_error_when_mastery_level_missing_level_field():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["nodes"][0]["mastery"]["levels"][0]["level"]
    with pytest.raises(SchemaValidationError, match="'level'"):
        validator.validate(payload)


def test_should_raise_error_when_mastery_level_is_invalid():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["nodes"][0]["mastery"]["levels"][0]["level"] = 99
    with pytest.raises(SchemaValidationError, match="invalid value: 99"):
        validator.validate(payload)


def test_should_raise_error_when_mastery_level_is_not_int():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["nodes"][0]["mastery"]["levels"][0]["level"] = "high"
    with pytest.raises(SchemaValidationError, match="must be an integer"):
        validator.validate(payload)


def test_should_raise_error_when_node_prerequisites_is_not_list():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["nodes"][0]["prerequisites"] = "fractions"
    with pytest.raises(SchemaValidationError, match="'prerequisites' must be a list"):
        validator.validate(payload)


# ── Failure cases — edges ─────────────────────────────────────────────────────


def test_should_raise_error_when_edge_is_not_dict():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["edges"] = ["not-a-dict"]
    with pytest.raises(SchemaValidationError, match="Edge at index 0 must be a dictionary"):
        validator.validate(payload)


def test_should_raise_error_when_edge_missing_type():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["edges"][0]["type"]
    with pytest.raises(SchemaValidationError, match="'type'"):
        validator.validate(payload)


def test_should_raise_error_when_edge_missing_source():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["edges"][0]["source"]
    with pytest.raises(SchemaValidationError, match="'source'"):
        validator.validate(payload)


def test_should_raise_error_when_edge_missing_target():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["edges"][0]["target"]
    with pytest.raises(SchemaValidationError, match="'target'"):
        validator.validate(payload)


def test_should_raise_error_when_edge_type_is_invalid():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["edges"][0]["type"] = "unknown_type"
    with pytest.raises(SchemaValidationError, match="invalid value"):
        validator.validate(payload)


def test_should_raise_error_when_edge_source_is_not_string():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["edges"][0]["source"] = 123
    with pytest.raises(SchemaValidationError, match="'source' must be a string"):
        validator.validate(payload)


# ── Failure cases — profiles ──────────────────────────────────────────────────


def test_should_raise_error_when_profile_is_not_dict():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["profiles"] = ["not-a-dict"]
    with pytest.raises(SchemaValidationError, match="Profile at index 0 must be a dictionary"):
        validator.validate(payload)


def test_should_raise_error_when_profile_missing_id():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["profiles"][0]["id"]
    with pytest.raises(SchemaValidationError, match="'id'"):
        validator.validate(payload)


def test_should_raise_error_when_profile_missing_name():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    del payload["profiles"][0]["name"]
    with pytest.raises(SchemaValidationError, match="'name'"):
        validator.validate(payload)


def test_should_raise_error_when_profile_required_nodes_is_not_list():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["profiles"][0]["required_nodes"] = "not-a-list"
    with pytest.raises(SchemaValidationError, match="'required_nodes' must be a list"):
        validator.validate(payload)


def test_should_raise_error_when_profile_mastery_targets_has_invalid_level():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["profiles"][0]["mastery_targets"] = {"math.arithmetic.fractions": 99}
    with pytest.raises(SchemaValidationError, match="invalid level"):
        validator.validate(payload)


def test_should_raise_error_when_profile_mastery_targets_is_not_dict():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["profiles"][0]["mastery_targets"] = [1, 2, 3]
    with pytest.raises(SchemaValidationError, match="'mastery_targets' must be a dictionary"):
        validator.validate(payload)


def test_should_raise_error_when_profile_node_weights_is_not_dict():
    validator = GraphSchemaValidator()
    payload = make_valid_payload()
    payload["profiles"][0]["node_weights"] = "heavy"
    with pytest.raises(SchemaValidationError, match="'node_weights' must be a dictionary"):
        validator.validate(payload)
