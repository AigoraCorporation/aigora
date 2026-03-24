import pytest

from curriculum_graph.domain.enums import EdgeType
from curriculum_graph.domain.models import (
    CanonicalGraph,
    CanonicalNode,
    CurriculumProfile,
    ErrorTaxonomyEntry,
    MasteryCriteria,
    PrerequisiteEdge,
    ProfileNode,
)
from curriculum_graph.application.validators import (
    StructuralValidator,
    ValidationReport,
    validate_graph,
)


# ── Factories ─────────────────────────────────────────────────────────────────


def _mc() -> MasteryCriteria:
    return MasteryCriteria("L1", "L2", "L3", "L4", "L5")


def _err() -> tuple:
    return (ErrorTaxonomyEntry("Error A", "Student makes a specific mistake here."),)


def _node(id: str, prereqs: tuple = (), regressions: tuple = ()) -> CanonicalNode:
    return CanonicalNode(
        id=id,
        name="Test Node",
        domain="algebra",
        description="A well-scoped math concept.",
        mastery_criteria=_mc(),
        error_taxonomy=_err(),
        prerequisite_ids=prereqs,
        regression_ids=regressions,
    )


def _empty_graph() -> CanonicalGraph:
    return CanonicalGraph(version="1.0.0", published_at="2026-01-01", nodes={}, profiles={})


def _profile(id="profile.test", required=(), path=()) -> CurriculumProfile:
    return CurriculumProfile(
        id=id,
        name="Test",
        version="1.0.0",
        requires_graph_version="1.0.0",
        required_nodes=required,
        progression_path=path,
        exam_skill_overlay=(),
    )


# ── S2: ID Format ─────────────────────────────────────────────────────────────


class TestS2IDFormat:
    def test_valid_node_id_passes(self):
        g = _empty_graph()
        g.nodes["algebra.arithmetic.operations"] = _node("algebra.arithmetic.operations")
        errors = StructuralValidator().validate(g)
        assert not [e for e in errors if e.code == "S2"]

    def test_uppercase_segment_fails(self):
        g = _empty_graph()
        bad = "Algebra.arithmetic.operations"
        g.nodes[bad] = _node(bad)
        errors = StructuralValidator().validate(g)
        assert any(e.code == "S2" for e in errors)

    def test_two_segment_id_fails(self):
        g = _empty_graph()
        bad = "algebra.operations"
        g.nodes[bad] = _node(bad)
        assert any(e.code == "S2" for e in StructuralValidator().validate(g))

    def test_underscore_in_id_fails(self):
        g = _empty_graph()
        bad = "algebra.arithmetic.integer_operations"
        g.nodes[bad] = _node(bad)
        assert any(e.code == "S2" for e in StructuralValidator().validate(g))

    def test_valid_profile_id_passes(self):
        g = _empty_graph()
        g.profiles["profile.fuvest"] = _profile("profile.fuvest")
        assert not [e for e in StructuralValidator().validate(g) if e.code == "S2"]

    def test_profile_id_missing_prefix_fails(self):
        g = _empty_graph()
        g.profiles["fuvest"] = _profile("fuvest")
        assert any(e.code == "S2" for e in StructuralValidator().validate(g))

    def test_hyphen_in_segment_is_valid(self):
        g = _empty_graph()
        g.nodes["algebra.equations.linear-one-variable"] = _node(
            "algebra.equations.linear-one-variable"
        )
        assert not [e for e in StructuralValidator().validate(g) if e.code == "S2"]


# ── S3: Required Fields ───────────────────────────────────────────────────────


class TestS3RequiredFields:
    def test_empty_name_fails(self):
        g = _empty_graph()
        node = CanonicalNode(
            id="algebra.a.b",
            name="",
            domain="algebra",
            description="desc",
            mastery_criteria=_mc(),
            error_taxonomy=_err(),
            prerequisite_ids=(),
            regression_ids=(),
        )
        g.nodes["algebra.a.b"] = node
        assert any(e.code == "S3" for e in StructuralValidator().validate(g))

    def test_empty_description_fails(self):
        g = _empty_graph()
        node = CanonicalNode(
            id="algebra.a.b",
            name="Node",
            domain="algebra",
            description="",
            mastery_criteria=_mc(),
            error_taxonomy=_err(),
            prerequisite_ids=(),
            regression_ids=(),
        )
        g.nodes["algebra.a.b"] = node
        assert any(e.code == "S3" for e in StructuralValidator().validate(g))

    def test_empty_mastery_level_fails(self):
        g = _empty_graph()
        mc_with_gap = MasteryCriteria(level_1="L1", level_2="", level_3="L3", level_4="L4", level_5="L5")
        node = CanonicalNode(
            id="algebra.a.b",
            name="Node",
            domain="algebra",
            description="Desc.",
            mastery_criteria=mc_with_gap,
            error_taxonomy=_err(),
            prerequisite_ids=(),
            regression_ids=(),
        )
        g.nodes["algebra.a.b"] = node
        assert any(e.code == "S3" for e in StructuralValidator().validate(g))

    def test_missing_error_taxonomy_fails(self):
        g = _empty_graph()
        node = CanonicalNode(
            id="algebra.a.b",
            name="Node",
            domain="algebra",
            description="Desc.",
            mastery_criteria=_mc(),
            error_taxonomy=(),
            prerequisite_ids=(),
            regression_ids=(),
        )
        g.nodes["algebra.a.b"] = node
        assert any(e.code == "S3" for e in StructuralValidator().validate(g))

    def test_empty_domain_fails(self):
        g = _empty_graph()
        node = CanonicalNode(
            id="algebra.a.b",
            name="Node",
            domain="",
            description="desc",
            mastery_criteria=_mc(),
            error_taxonomy=_err(),
            prerequisite_ids=(),
            regression_ids=(),
        )
        g.nodes["algebra.a.b"] = node
        assert any(e.code == "S3" for e in StructuralValidator().validate(g))

    def test_valid_node_has_no_s3_errors(self):
        g = _empty_graph()
        g.nodes["algebra.a.b"] = _node("algebra.a.b")
        assert not [e for e in StructuralValidator().validate(g) if e.code == "S3"]


# ── S4: Acyclicity ────────────────────────────────────────────────────────────


class TestS4Acyclicity:
    def test_linear_chain_passes(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.nodes["algebra.a.two"] = _node(
            "algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
        )
        assert not [e for e in StructuralValidator().validate(g) if e.code == "S4"]

    def test_direct_cycle_fails(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node(
            "algebra.a.one",
            prereqs=(PrerequisiteEdge("algebra.a.two", EdgeType.HARD),),
        )
        g.nodes["algebra.a.two"] = _node(
            "algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
        )
        assert any(e.code == "S4" for e in StructuralValidator().validate(g))

    def test_transitive_cycle_fails(self):
        g = _empty_graph()
        # A → B → C → A
        g.nodes["algebra.a.one"] = _node(
            "algebra.a.one",
            prereqs=(PrerequisiteEdge("algebra.a.three", EdgeType.HARD),),
        )
        g.nodes["algebra.a.two"] = _node(
            "algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
        )
        g.nodes["algebra.a.three"] = _node(
            "algebra.a.three",
            prereqs=(PrerequisiteEdge("algebra.a.two", EdgeType.HARD),),
        )
        assert any(e.code == "S4" for e in StructuralValidator().validate(g))


# ── S5: Referential Integrity ─────────────────────────────────────────────────


class TestS5ReferentialIntegrity:
    def test_valid_references_pass(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.nodes["algebra.a.two"] = _node(
            "algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
            regressions=("algebra.a.one",),
        )
        assert not [e for e in StructuralValidator().validate(g) if e.code == "S5"]

    def test_dangling_prerequisite_fails(self):
        g = _empty_graph()
        g.nodes["algebra.a.two"] = _node(
            "algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.missing", EdgeType.HARD),),
        )
        assert any(e.code == "S5" for e in StructuralValidator().validate(g))

    def test_dangling_regression_fails(self):
        g = _empty_graph()
        g.nodes["algebra.a.two"] = _node(
            "algebra.a.two",
            regressions=("algebra.a.missing",),
        )
        assert any(e.code == "S5" for e in StructuralValidator().validate(g))

    def test_dangling_profile_required_node_fails(self):
        g = _empty_graph()
        g.profiles["profile.test"] = _profile(
            required=(ProfileNode("algebra.a.missing", 3, 1.0),)
        )
        assert any(e.code == "S5" for e in StructuralValidator().validate(g))

    def test_dangling_progression_path_ref_fails(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.profiles["profile.test"] = _profile(
            required=(ProfileNode("algebra.a.one", 3, 1.0),),
            path=("algebra.a.one", "algebra.a.ghost"),  # ghost not in nodes
        )
        assert any(e.code == "S5" for e in StructuralValidator().validate(g))


# ── S6: Progression Path Order ────────────────────────────────────────────────


class TestS6ProgressionPathOrder:
    def test_correct_order_passes(self):
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
        assert not [e for e in StructuralValidator().validate(g) if e.code == "S6"]

    def test_inverted_order_fails(self):
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
            # Wrong order: dependent before prerequisite
            path=("algebra.a.two", "algebra.a.one"),
        )
        assert any(e.code == "S6" for e in StructuralValidator().validate(g))

    def test_hard_prereq_outside_path_is_skipped(self):
        """Hard prereq of a path node that is NOT in the path is silently skipped by S6
        (SE7 handles the human-review aspect). No S6 error should be raised."""
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.nodes["algebra.a.two"] = _node(
            "algebra.a.two",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
        )
        # Profile includes 'two' in path but 'one' is not in progression_path.
        g.profiles["profile.test"] = _profile(
            required=(
                ProfileNode("algebra.a.one", 3, 1.0),
                ProfileNode("algebra.a.two", 3, 1.0),
            ),
            path=("algebra.a.two",),  # prereq 'one' absent from path — S6 must skip it
        )
        assert not [e for e in StructuralValidator().validate(g) if e.code == "S6"]


# ── S7: Mastery Target Bounds ─────────────────────────────────────────────────


class TestS7MasteryTargetBounds:
    def _graph_with_target(self, target: int) -> CanonicalGraph:
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.profiles["profile.test"] = _profile(
            required=(ProfileNode("algebra.a.one", target, 1.0),),
            path=("algebra.a.one",),
        )
        return g

    def test_target_1_passes(self):
        assert not [e for e in StructuralValidator().validate(self._graph_with_target(1)) if e.code == "S7"]

    def test_target_5_passes(self):
        assert not [e for e in StructuralValidator().validate(self._graph_with_target(5)) if e.code == "S7"]

    def test_target_0_fails(self):
        assert any(e.code == "S7" for e in StructuralValidator().validate(self._graph_with_target(0)))

    def test_target_6_fails(self):
        assert any(e.code == "S7" for e in StructuralValidator().validate(self._graph_with_target(6)))


# ── S8: Weight Non-Negativity ─────────────────────────────────────────────────


class TestS8WeightNonNegativity:
    def _graph_with_weight(self, weight: float) -> CanonicalGraph:
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        g.profiles["profile.test"] = _profile(
            required=(ProfileNode("algebra.a.one", 3, weight),),
            path=("algebra.a.one",),
        )
        return g

    def test_positive_weight_passes(self):
        assert not [e for e in StructuralValidator().validate(self._graph_with_weight(0.5)) if e.code == "S8"]

    def test_zero_weight_fails(self):
        assert any(e.code == "S8" for e in StructuralValidator().validate(self._graph_with_weight(0.0)))

    def test_negative_weight_fails(self):
        assert any(e.code == "S8" for e in StructuralValidator().validate(self._graph_with_weight(-1.0)))


# ── validate_graph convenience ────────────────────────────────────────────────


class TestValidateGraph:
    def test_returns_report_with_no_errors_for_valid_graph(self):
        g = _empty_graph()
        g.nodes["algebra.a.one"] = _node("algebra.a.one")
        report = validate_graph(g)
        assert isinstance(report, ValidationReport)
        assert not report.has_errors

    def test_returns_report_with_errors_for_invalid_graph(self):
        g = _empty_graph()
        bad_id = "BadId"
        g.nodes[bad_id] = _node(bad_id)
        report = validate_graph(g)
        assert report.has_errors

    def test_report_str_shows_errors(self):
        g = _empty_graph()
        bad_id = "BadId"
        g.nodes[bad_id] = _node(bad_id)
        report = validate_graph(g)
        assert "S2" in str(report)
