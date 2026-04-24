import pytest

from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.enums import MasteryLevel


def test_should_create_curriculum_profile_successfully():
    profile = CurriculumProfile(
        id="sat-math",
        name="SAT Math",
        required_nodes={"fractions", "equations"},
        mastery_targets={"fractions": MasteryLevel.INDEPENDENT},
        node_weights={"fractions": 1.5},
        progression_path=["fractions", "equations"],
    )

    assert profile.id == "sat-math"
    assert profile.name == "SAT Math"


def test_should_raise_error_when_profile_id_is_empty():
    with pytest.raises(ValueError, match="CurriculumProfile id must be non-empty."):
        CurriculumProfile(
            id="",
            name="SAT Math",
        )


def test_should_raise_error_when_profile_name_is_empty():
    with pytest.raises(ValueError, match="CurriculumProfile name must be non-empty."):
        CurriculumProfile(
            id="sat-math",
            name="",
        )


def test_should_raise_error_when_node_weight_is_negative():
    with pytest.raises(ValueError, match="Node weight must be non-negative. node_id=fractions"):
        CurriculumProfile(
            id="sat-math",
            name="SAT Math",
            node_weights={"fractions": -1.0},
        )


def test_should_raise_error_when_node_weights_contains_empty_node_id():
    with pytest.raises(
        ValueError,
        match="CurriculumProfile node_weights cannot contain empty node ids.",
    ):
        CurriculumProfile(
            id="sat-math",
            name="SAT Math",
            node_weights={"": 1.0},
        )


def test_should_raise_error_when_mastery_targets_contains_empty_node_id():
    with pytest.raises(
        ValueError,
        match="CurriculumProfile mastery_targets cannot contain empty node ids.",
    ):
        CurriculumProfile(
            id="sat-math",
            name="SAT Math",
            mastery_targets={"": MasteryLevel.GUIDED},
        )


def test_should_raise_error_when_progression_path_contains_empty_node_id():
    with pytest.raises(
        ValueError,
        match="CurriculumProfile progression_path cannot contain empty node ids.",
    ):
        CurriculumProfile(
            id="sat-math",
            name="SAT Math",
            progression_path=["fractions", ""],
        )


def test_should_return_all_referenced_node_ids():
    profile = CurriculumProfile(
        id="sat-math",
        name="SAT Math",
        required_nodes={"fractions"},
        mastery_targets={"equations": MasteryLevel.INDEPENDENT},
        node_weights={"algebra": 2.0},
        progression_path=["geometry"],
    )

    assert profile.referenced_node_ids() == {
        "fractions",
        "equations",
        "algebra",
        "geometry",
    }