import pytest

from curriculum_graph.domain.enums import EdgeType, NodeStatus, ProfileStatus
from curriculum_graph.domain.models import (
    CanonicalNode,
    CurriculumProfile,
    ErrorTaxonomyEntry,
    MasteryCriteria,
    PrerequisiteEdge,
    ProfileNode,
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _mc(**overrides) -> MasteryCriteria:
    defaults = dict(level_1="L1", level_2="L2", level_3="L3", level_4="L4", level_5="L5")
    defaults.update(overrides)
    return MasteryCriteria(**defaults)


def _node(id: str = "algebra.arithmetic.operations", **overrides) -> CanonicalNode:
    defaults = dict(
        id=id,
        name="Operations",
        domain="algebra",
        description="Basic arithmetic operations.",
        mastery_criteria=_mc(),
        error_taxonomy=(ErrorTaxonomyEntry("Sign error", "Student inverts the sign."),),
        prerequisite_ids=(),
        regression_ids=(),
    )
    defaults.update(overrides)
    return CanonicalNode(**defaults)


# ── MasteryCriteria ───────────────────────────────────────────────────────────


class TestMasteryCriteria:
    def test_for_level_returns_correct_text(self):
        mc = MasteryCriteria(level_1="L1", level_2="L2", level_3="L3", level_4="L4", level_5="L5")
        assert mc.for_level(1) == "L1"
        assert mc.for_level(3) == "L3"
        assert mc.for_level(5) == "L5"

    def test_for_level_raises_on_zero(self):
        mc = _mc()
        with pytest.raises(ValueError):
            mc.for_level(0)

    def test_for_level_raises_on_six(self):
        mc = _mc()
        with pytest.raises(ValueError):
            mc.for_level(6)

    def test_as_dict_returns_all_levels(self):
        mc = _mc()
        d = mc.as_dict()
        assert set(d.keys()) == {1, 2, 3, 4, 5}


# ── CanonicalNode ─────────────────────────────────────────────────────────────


class TestCanonicalNode:
    def test_default_status_is_active(self):
        node = _node()
        assert node.status == NodeStatus.ACTIVE

    def test_node_is_frozen(self):
        node = _node()
        with pytest.raises((AttributeError, TypeError)):
            node.name = "Changed"  # type: ignore[misc]

    def test_no_prerequisites_by_default(self):
        node = _node()
        assert node.prerequisite_ids == ()
        assert node.regression_ids == ()

    def test_deprecated_node_has_status_deprecated(self):
        node = _node(status=NodeStatus.DEPRECATED, deprecated_since="2026-01-01")
        assert node.status == NodeStatus.DEPRECATED
        assert node.deprecated_since == "2026-01-01"

    def test_replaced_by_defaults_to_none(self):
        node = _node()
        assert node.replaced_by is None


# ── PrerequisiteEdge ──────────────────────────────────────────────────────────


class TestPrerequisiteEdge:
    def test_edge_is_frozen(self):
        edge = PrerequisiteEdge(node_id="algebra.a.one", edge_type=EdgeType.HARD)
        with pytest.raises((AttributeError, TypeError)):
            edge.node_id = "changed"  # type: ignore[misc]

    def test_edge_type_hard(self):
        edge = PrerequisiteEdge(node_id="algebra.a.one", edge_type=EdgeType.HARD)
        assert edge.edge_type == EdgeType.HARD

    def test_edge_type_soft(self):
        edge = PrerequisiteEdge(node_id="algebra.a.one", edge_type=EdgeType.SOFT)
        assert edge.edge_type == EdgeType.SOFT


# ── CurriculumProfile ─────────────────────────────────────────────────────────


class TestCurriculumProfile:
    def _profile(self) -> CurriculumProfile:
        return CurriculumProfile(
            id="profile.test",
            name="Test",
            version="1.0.0",
            requires_graph_version="1.0.0",
            required_nodes=(
                ProfileNode(node_id="algebra.arithmetic.operations", mastery_target=3, weight=1.0),
                ProfileNode(node_id="algebra.equations.linear", mastery_target=4, weight=1.5),
            ),
            progression_path=("algebra.arithmetic.operations", "algebra.equations.linear"),
            exam_skill_overlay=(),
        )

    def test_required_node_ids_returns_frozenset(self):
        profile = self._profile()
        ids = profile.required_node_ids()
        assert isinstance(ids, frozenset)
        assert "algebra.arithmetic.operations" in ids
        assert "algebra.equations.linear" in ids

    def test_mastery_target_for_known_node(self):
        profile = self._profile()
        assert profile.mastery_target_for("algebra.arithmetic.operations") == 3
        assert profile.mastery_target_for("algebra.equations.linear") == 4

    def test_mastery_target_for_unknown_returns_none(self):
        profile = self._profile()
        assert profile.mastery_target_for("algebra.unknown.node") is None

    def test_weight_for_known_node(self):
        profile = self._profile()
        assert profile.weight_for("algebra.equations.linear") == 1.5

    def test_weight_for_unknown_returns_none(self):
        profile = self._profile()
        assert profile.weight_for("algebra.unknown.node") is None

    def test_default_status_is_active(self):
        profile = self._profile()
        assert profile.status == ProfileStatus.ACTIVE

    def test_profile_is_frozen(self):
        profile = self._profile()
        with pytest.raises((AttributeError, TypeError)):
            profile.name = "Changed"  # type: ignore[misc]
