"""
Tests for SemanticValidator and OperationalValidator, covering the cases
that fire review hooks and structural errors from the operational layer.
"""
import pytest

from curriculum_graph.domain.enums import EdgeType
from curriculum_graph.domain.models import (
    CanonicalGraph,
    CanonicalNode,
    CurriculumProfile,
    ErrorTaxonomyEntry,
    ExamSkillOverlayEntry,
    MasteryCriteria,
    PrerequisiteEdge,
    ProfileNode,
)
from curriculum_graph.application.validators import (
    OperationalValidator,
    SemanticValidator,
    validate_graph,
)


# ── Factories ─────────────────────────────────────────────────────────────────


def _mc(**overrides) -> MasteryCriteria:
    defaults = dict(level_1="L1", level_2="L2", level_3="L3", level_4="L4", level_5="L5")
    defaults.update(overrides)
    return MasteryCriteria(**defaults)


def _err(description="Student confuses specific sign rule in this operation.") -> tuple:
    return (ErrorTaxonomyEntry("Sign error", description),)


def _node(
    id: str = "algebra.a.one",
    description: str = "A well-scoped mathematical concept.",
    regression_ids: tuple = (),
    prereqs: tuple = (),
    mc: MasteryCriteria = None,
    error_taxonomy: tuple = None,
) -> CanonicalNode:
    return CanonicalNode(
        id=id,
        name="Node",
        domain="algebra",
        description=description,
        mastery_criteria=mc or _mc(),
        error_taxonomy=error_taxonomy or _err(),
        prerequisite_ids=prereqs,
        regression_ids=regression_ids,
    )


def _empty_graph() -> CanonicalGraph:
    return CanonicalGraph(version="1.0.0", published_at="2026-01-01", nodes={}, profiles={})


def _profile(
    id="profile.test",
    required=(),
    path=(),
    overlay=(),
) -> CurriculumProfile:
    return CurriculumProfile(
        id=id,
        name="Test",
        version="1.0.0",
        requires_graph_version="1.0.0",
        required_nodes=required,
        progression_path=path,
        exam_skill_overlay=overlay,
    )


# ── SE2: Description exam-neutrality ─────────────────────────────────────────


class TestSE2DescriptionExamNeutrality:
    def test_description_mentioning_fuvest_fires_hook(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node(description="This concept appears in the fuvest exam.")
        hooks = SemanticValidator().validate(g)
        assert any(h.code == "SE2" for h in hooks)

    def test_description_mentioning_enem_fires_hook(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node(description="Frequently tested in ENEM vestibular.")
        hooks = SemanticValidator().validate(g)
        assert any(h.code == "SE2" for h in hooks)

    def test_neutral_description_does_not_fire_hook(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node(description="A pure mathematics concept without exam references.")
        hooks = SemanticValidator().validate(g)
        assert not any(h.code == "SE2" for h in hooks)


# ── SE3: Mastery criteria gradation ──────────────────────────────────────────


class TestSE3MasteryGradation:
    def test_duplicate_level_texts_fire_hook(self):
        g = _empty_graph()
        # Level 1 and level 2 have identical text
        dupe_mc = _mc(level_1="Same text.", level_2="Same text.")
        g.nodes["algebra.a.one"] = _node(mc=dupe_mc)
        hooks = SemanticValidator().validate(g)
        assert any(h.code == "SE3" for h in hooks)

    def test_all_distinct_levels_do_not_fire_hook(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node(mc=_mc())
        hooks = SemanticValidator().validate(g)
        assert not any(h.code == "SE3" for h in hooks)


# ── SE4: Error taxonomy specificity ──────────────────────────────────────────


class TestSE4ErrorTaxonomySpecificity:
    def test_generic_phrase_fires_hook(self):
        g = _empty_graph()
        generic_err = (ErrorTaxonomyEntry("Generic", "Student may make calculation errors here."),)
        g.nodes["algebra.a.one"] = _node(error_taxonomy=generic_err)
        hooks = SemanticValidator().validate(g)
        assert any(h.code == "SE4" for h in hooks)

    def test_specific_error_description_does_not_fire_hook(self):
        g = _empty_graph()
        specific_err = (
            ErrorTaxonomyEntry(
                "Sign transposition",
                "Student moves a term across the equals sign without inverting its sign.",
            ),
        )
        g.nodes["algebra.a.one"] = _node(error_taxonomy=specific_err)
        hooks = SemanticValidator().validate(g)
        assert not any(h.code == "SE4" for h in hooks)


# ── SE6: Regression path relevance ───────────────────────────────────────────


class TestSE6RegressionPathRelevance:
    def test_node_with_no_regression_ids_fires_hook(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node(regression_ids=())
        hooks = SemanticValidator().validate(g)
        assert any(h.code == "SE6" for h in hooks)

    def test_node_with_regression_ids_does_not_fire_hook(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node()
        g.nodes["algebra.a.two"] = _node(
            id="algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
            regression_ids=("algebra.a.one",),
        )
        hooks = SemanticValidator().validate(g)
        se6_hooks = [h for h in hooks if h.code == "SE6"]
        assert not any(h.node_id == "algebra.a.two" for h in se6_hooks)


# ── SE7: Profile prerequisite completeness ────────────────────────────────────


class TestSE7ProfilePrerequisiteCompleteness:
    def test_profile_omitting_hard_prereq_fires_hook(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.nodes["algebra.a.two"] = _node(
            id="algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
        )
        # Profile only includes "two" but omits its hard prerequisite "one"
        g.profiles["profile.test"] = _profile(
            required=(ProfileNode("algebra.a.two", 3, 1.0),),
            path=("algebra.a.two",),
        )
        hooks = SemanticValidator().validate(g)
        assert any(h.code == "SE7" for h in hooks)

    def test_profile_including_hard_prereq_does_not_fire_hook(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.nodes["algebra.a.two"] = _node(
            id="algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
        )
        g.profiles["profile.test"] = _profile(
            required=(
                ProfileNode("algebra.a.one", 3, 1.0),
                ProfileNode("algebra.a.two", 3, 1.0),
            ),
            path=("algebra.a.one", "algebra.a.two"),
        )
        hooks = SemanticValidator().validate(g)
        assert not any(h.code == "SE7" for h in hooks)

    def test_soft_prereq_omitted_from_profile_does_not_fire_hook(self):
        """SE7 only checks hard prerequisites."""
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.nodes["algebra.a.two"] = _node(
            id="algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.SOFT),),
        )
        g.profiles["profile.test"] = _profile(
            required=(ProfileNode("algebra.a.two", 3, 1.0),),
            path=("algebra.a.two",),
        )
        hooks = SemanticValidator().validate(g)
        assert not any(h.code == "SE7" for h in hooks)

    def test_required_node_absent_from_graph_is_skipped_gracefully(self):
        """SE7 defensive path: profile required_node not in graph.nodes → skip."""
        g = _empty_graph()
        # Profile declares a node that does not exist in graph.nodes.
        # SE7 must not raise; it continues past the missing node.
        g.profiles["profile.test"] = _profile(
            required=(ProfileNode("algebra.a.ghost", 3, 1.0),),
            path=("algebra.a.ghost",),
        )
        hooks = SemanticValidator().validate(g)
        # No SE7 hook fires for a node that can't be looked up.
        assert not any(h.code == "SE7" for h in hooks)


# ── SE8: Exam skill overlay containment ───────────────────────────────────────


class TestSE8ExamSkillOverlayContainment:
    def test_math_keyword_in_overlay_name_fires_hook(self):
        g = _empty_graph()
        overlay = (ExamSkillOverlayEntry(
            name="Quadratic equation solving speed",
            description="Solve parabola problems faster.",
        ),)
        g.profiles["profile.test"] = _profile(overlay=overlay)
        hooks = SemanticValidator().validate(g)
        assert any(h.code == "SE8" for h in hooks)

    def test_math_keyword_in_overlay_description_fires_hook(self):
        g = _empty_graph()
        overlay = (ExamSkillOverlayEntry(
            name="Time management",
            description="Efficiently handle algebra problems under pressure.",
        ),)
        g.profiles["profile.test"] = _profile(overlay=overlay)
        hooks = SemanticValidator().validate(g)
        assert any(h.code == "SE8" for h in hooks)

    def test_non_math_overlay_does_not_fire_hook(self):
        g = _empty_graph()
        overlay = (ExamSkillOverlayEntry(
            name="Time pressure management",
            description="Recognise when to skip a problem to optimise exam score.",
        ),)
        g.profiles["profile.test"] = _profile(overlay=overlay)
        hooks = SemanticValidator().validate(g)
        assert not any(h.code == "SE8" for h in hooks)


# ── OperationalValidator ──────────────────────────────────────────────────────


class TestOperationalValidator:
    def _make_graph_with_disconnected_node(self) -> CanonicalGraph:
        """A graph where 'three' has 'two' as a prerequisite, but 'two' is not in the graph."""
        g = _empty_graph()
        # "one" is a root; "three" declares "two" as hard prereq, but "two" doesn't exist.
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.nodes["algebra.a.three"] = _node(
            "algebra.a.three",
            prereqs=(PrerequisiteEdge("algebra.a.two", EdgeType.HARD),),
        )
        return g

    def test_o1_unreachable_node_in_profile_fails(self):
        g = self._make_graph_with_disconnected_node()
        g.nodes["algebra.a.two"] = _node("algebra.a.two")
        # "three" requires "two", which requires nothing — but let's make a gap:
        # Profile requires "three" but the prerequisite chain has a broken link.
        # Remove "two" again to create a true gap.
        del g.nodes["algebra.a.two"]
        # Add the profile requiring the unreachable node
        g.profiles["profile.test"] = _profile(
            required=(ProfileNode("algebra.a.three", 3, 1.0),),
            path=("algebra.a.three",),
        )
        errors = OperationalValidator().validate(g)
        assert any(e.code == "O1" for e in errors)

    def test_o1_reachable_node_passes(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.nodes["algebra.a.two"] = _node(
            "algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
        )
        g.profiles["profile.test"] = _profile(
            required=(
                ProfileNode("algebra.a.one", 3, 1.0),
                ProfileNode("algebra.a.two", 3, 1.0),
            ),
            path=("algebra.a.one", "algebra.a.two"),
        )
        errors = OperationalValidator().validate(g)
        assert not any(e.code == "O1" for e in errors)

    def test_o2_node_with_invalid_key_characters_fails(self):
        g = _empty_graph()
        bad_id = "algebra.a.one (special)"
        g.nodes[bad_id] = _node(bad_id)
        errors = OperationalValidator().validate(g)
        assert any(e.code == "O2" for e in errors)

    def test_o2_valid_node_id_passes(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        errors = OperationalValidator().validate(g)
        assert not any(e.code == "O2" for e in errors)

    def test_o3_mastery_target_above_5_fails(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.profiles["profile.test"] = _profile(
            required=(ProfileNode("algebra.a.one", 6, 1.0),),
        )
        errors = OperationalValidator().validate(g)
        assert any(e.code == "O3" for e in errors)

    def test_o3_mastery_target_at_5_passes(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.profiles["profile.test"] = _profile(
            required=(ProfileNode("algebra.a.one", 5, 1.0),),
        )
        errors = OperationalValidator().validate(g)
        assert not any(e.code == "O3" for e in errors)


# ── validate_graph with operational=True ──────────────────────────────────────


class TestValidateGraphOperational:
    def test_operational_flag_runs_operational_validators(self):
        g = _empty_graph()
        bad_id = "algebra.a.one (invalid)"
        g.nodes[bad_id] = _node(bad_id)
        report = validate_graph(g, operational=True)
        # S2 fires (bad id format), O2 fires (bad key)
        codes = {e.code for e in report.errors}
        assert "S2" in codes
        assert "O2" in codes

    def test_operational_flag_false_skips_operational_validators(self):
        g = _empty_graph()
        bad_id = "algebra.a.one (invalid)"
        g.nodes[bad_id] = _node(bad_id)
        report = validate_graph(g, operational=False)
        # Only S2 fires; O2 is skipped
        codes = {e.code for e in report.errors}
        assert "S2" in codes
        assert "O2" not in codes

    def test_clean_graph_passes_all_validators(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        report = validate_graph(g, operational=True)
        # SE6 fires for the node with no regression_ids — but that's a review hook, not an error
        assert not report.has_errors
