from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType

import pytest


def test_should_create_edge_successfully():
    edge = Edge(
        type=EdgeType.HARD_PREREQUISITE,
        source="fractions",
        target="equations",
    )

    assert edge.type == EdgeType.HARD_PREREQUISITE
    assert edge.source == "fractions"
    assert edge.target == "equations"


def test_should_raise_error_when_source_is_empty():
    with pytest.raises(ValueError, match="Edge source must be non-empty."):
        Edge(
            type=EdgeType.HARD_PREREQUISITE,
            source="",
            target="equations",
        )


def test_should_raise_error_when_target_is_empty():
    with pytest.raises(ValueError, match="Edge target must be non-empty."):
        Edge(
            type=EdgeType.HARD_PREREQUISITE,
            source="fractions",
            target="",
        )


def test_should_raise_error_when_source_and_target_are_equal():
    with pytest.raises(ValueError, match="Edge source and target must be different."):
        Edge(
            type=EdgeType.HARD_PREREQUISITE,
            source="fractions",
            target="fractions",
        )