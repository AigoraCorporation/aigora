import pytest

from aigora.curriculum_graph.domain.enums import MasteryLevel
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


def test_should_create_node_successfully():
    node = Node(
        id="fractions",
        name="Fractions",
        domain="arithmetic",
        description="Understand fraction representation and operations.",
        mastery_criteria=make_mastery_scale(),
    )

    assert node.id == "fractions"
    assert node.name == "Fractions"
    assert node.domain == "arithmetic"


def test_should_raise_error_when_id_is_empty():
    with pytest.raises(ValueError, match="Node id must be non-empty."):
        Node(
            id="",
            name="Fractions",
            domain="arithmetic",
            description="Description",
            mastery_criteria=make_mastery_scale(),
        )


def test_should_raise_error_when_name_is_empty():
    with pytest.raises(ValueError, match="Node name must be non-empty."):
        Node(
            id="fractions",
            name="",
            domain="arithmetic",
            description="Description",
            mastery_criteria=make_mastery_scale(),
        )


def test_should_raise_error_when_domain_is_empty():
    with pytest.raises(ValueError, match="Node domain must be non-empty."):
        Node(
            id="fractions",
            name="Fractions",
            domain="",
            description="Description",
            mastery_criteria=make_mastery_scale(),
        )


def test_should_raise_error_when_description_is_empty():
    with pytest.raises(ValueError, match="Node description must be non-empty."):
        Node(
            id="fractions",
            name="Fractions",
            domain="arithmetic",
            description="",
            mastery_criteria=make_mastery_scale(),
        )


def test_should_raise_error_when_node_lists_itself_as_prerequisite():
    with pytest.raises(ValueError, match="Node cannot list itself as prerequisite."):
        Node(
            id="fractions",
            name="Fractions",
            domain="arithmetic",
            description="Description",
            mastery_criteria=make_mastery_scale(),
            prerequisite_ids=["fractions"],
        )


def test_should_raise_error_when_node_lists_itself_as_regression_target():
    with pytest.raises(ValueError, match="Node cannot list itself as regression target."):
        Node(
            id="fractions",
            name="Fractions",
            domain="arithmetic",
            description="Description",
            mastery_criteria=make_mastery_scale(),
            regression_ids=["fractions"],
        )


def test_should_raise_error_when_prerequisite_ids_contain_duplicates():
    with pytest.raises(ValueError, match="Node prerequisite_ids must not contain duplicates."):
        Node(
            id="fractions",
            name="Fractions",
            domain="arithmetic",
            description="Description",
            mastery_criteria=make_mastery_scale(),
            prerequisite_ids=["integers", "integers"],
        )


def test_should_raise_error_when_regression_ids_contain_duplicates():
    with pytest.raises(ValueError, match="Node regression_ids must not contain duplicates."):
        Node(
            id="fractions",
            name="Fractions",
            domain="arithmetic",
            description="Description",
            mastery_criteria=make_mastery_scale(),
            regression_ids=["integers", "integers"],
        )