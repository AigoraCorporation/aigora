from __future__ import annotations

import pytest

from aigora.curriculum_graph.domain.value_objects.node_id import NodeId
from aigora.curriculum_graph.domain.value_objects.profile_id import ProfileId


def test_node_id_should_keep_valid_value():
    assert NodeId("math.arithmetic.fractions") == "math.arithmetic.fractions"


def test_node_id_should_reject_blank_value():
    with pytest.raises(ValueError, match="Node id must be non-empty"):
        NodeId(" ")


def test_profile_id_should_keep_valid_value():
    assert ProfileId("profile.sat-math") == "profile.sat-math"


def test_profile_id_should_reject_blank_value():
    with pytest.raises(ValueError, match="CurriculumProfile id must be non-empty"):
        ProfileId(" ")
