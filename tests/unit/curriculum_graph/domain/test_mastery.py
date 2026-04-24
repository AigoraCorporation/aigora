import pytest

from aigora.curriculum_graph.domain.enums import MasteryLevel
from aigora.curriculum_graph.domain.mastery import MasteryCriterion, MasteryScale


def test_should_return_mastery_criterion_by_level():
    criterion = MasteryCriterion(
        level=MasteryLevel.INDEPENDENT,
        description="Solves standard problems independently.",
    )
    scale = MasteryScale(
        criteria_by_level={MasteryLevel.INDEPENDENT: criterion}
    )

    result = scale.get(MasteryLevel.INDEPENDENT)

    assert result == criterion


def test_should_return_true_when_scale_has_level():
    scale = MasteryScale(
        criteria_by_level={
            MasteryLevel.GUIDED: MasteryCriterion(
                level=MasteryLevel.GUIDED,
                description="Solves with guidance.",
            )
        }
    )

    assert scale.has_level(MasteryLevel.GUIDED) is True


def test_should_return_false_when_scale_does_not_have_level():
    scale = MasteryScale(criteria_by_level={})

    assert scale.has_level(MasteryLevel.GUIDED) is False


def test_should_raise_error_when_level_is_not_defined():
    scale = MasteryScale(criteria_by_level={})

    with pytest.raises(KeyError, match="Mastery level not defined"):
        scale.get(MasteryLevel.UNEXPOSED)


def test_should_validate_mastery_scale_successfully():
    scale = MasteryScale(
        criteria_by_level={
            MasteryLevel.RECOGNISES: MasteryCriterion(
                level=MasteryLevel.RECOGNISES,
                description="Recognises the concept.",
            )
        }
    )

    scale.validate()


def test_should_raise_error_when_mastery_scale_is_empty():
    scale = MasteryScale(criteria_by_level={})

    with pytest.raises(
        ValueError,
        match="Mastery scale must define at least one mastery criterion.",
    ):
        scale.validate()


def test_should_raise_error_when_dictionary_key_does_not_match_criterion_level():
    scale = MasteryScale(
        criteria_by_level={
            MasteryLevel.GUIDED: MasteryCriterion(
                level=MasteryLevel.INDEPENDENT,
                description="Invalid mapping.",
            )
        }
    )

    with pytest.raises(
        ValueError,
        match="Mastery scale is inconsistent: dictionary key must match criterion.level.",
    ):
        scale.validate()


def test_should_raise_error_when_criterion_description_is_empty():
    scale = MasteryScale(
        criteria_by_level={
            MasteryLevel.GUIDED: MasteryCriterion(
                level=MasteryLevel.GUIDED,
                description="   ",
            )
        }
    )

    with pytest.raises(
        ValueError,
        match="Mastery criterion for level MasteryLevel.GUIDED must have a non-empty description.",
    ):
        scale.validate()