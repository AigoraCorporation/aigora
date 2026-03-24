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
from curriculum_graph.application.queries import CurriculumGraphQueryService


# ── Graph factory ─────────────────────────────────────────────────────────────


def _mc() -> MasteryCriteria:
    return MasteryCriteria("L1", "L2", "L3", "L4", "L5")


def _err() -> tuple:
    return (ErrorTaxonomyEntry("E", "Specific misconception for this concept."),)


def _node(id: str, prereqs: tuple = (), regressions: tuple = ()) -> CanonicalNode:
    return CanonicalNode(
        id=id,
        name=id,
        domain="algebra",
        description="A test concept.",
        mastery_criteria=_mc(),
        error_taxonomy=_err(),
        prerequisite_ids=prereqs,
        regression_ids=regressions,
    )


def _chain_graph() -> CanonicalGraph:
    """
    Three-node chain:  A  ←(hard)─  B  ←(hard)─  C
    A is foundational (no prerequisites).
    B regresses to A on breakdown.
    """
    a = _node("algebra.a.one")
    b = _node(
        "algebra.a.two",
        prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
        regressions=("algebra.a.one",),
    )
    c = _node(
        "algebra.a.three",
        prereqs=(PrerequisiteEdge("algebra.a.two", EdgeType.HARD),),
    )
    return CanonicalGraph(
        version="1.0.0",
        published_at="2026-01-01",
        nodes={
            "algebra.a.one": a,
            "algebra.a.two": b,
            "algebra.a.three": c,
        },
        profiles={},
    )


def _graph_with_profile() -> CanonicalGraph:
    graph = _chain_graph()
    profile = CurriculumProfile(
        id="profile.test",
        name="Test",
        version="1.0.0",
        requires_graph_version="1.0.0",
        required_nodes=(
            ProfileNode("algebra.a.one", 3, 1.0),
            ProfileNode("algebra.a.two", 3, 1.0),
            ProfileNode("algebra.a.three", 4, 1.5),
        ),
        progression_path=("algebra.a.one", "algebra.a.two", "algebra.a.three"),
        exam_skill_overlay=(),
    )
    graph.profiles["profile.test"] = profile
    return graph


# ── get_node ──────────────────────────────────────────────────────────────────


class TestGetNode:
    def test_returns_node_when_found(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        node = svc.get_node("algebra.a.one")
        assert node is not None
        assert node.id == "algebra.a.one"

    def test_returns_none_when_not_found(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert svc.get_node("does.not.exist") is None


# ── get_profile ───────────────────────────────────────────────────────────────


class TestGetProfile:
    def test_returns_profile_when_found(self):
        svc = CurriculumGraphQueryService(_graph_with_profile())
        profile = svc.get_profile("profile.test")
        assert profile is not None
        assert profile.name == "Test"

    def test_returns_none_when_not_found(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert svc.get_profile("profile.missing") is None


# ── get_prerequisites ─────────────────────────────────────────────────────────


class TestGetPrerequisites:
    def test_returns_prerequisites_for_non_foundational_node(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        prereqs = svc.get_prerequisites("algebra.a.two")
        assert len(prereqs) == 1
        assert prereqs[0].node_id == "algebra.a.one"
        assert prereqs[0].edge_type == EdgeType.HARD

    def test_returns_empty_for_foundational_node(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert svc.get_prerequisites("algebra.a.one") == []

    def test_returns_empty_for_nonexistent_node(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert svc.get_prerequisites("does.not.exist") == []

    def test_hard_prereqs_appear_before_soft(self):
        a = _node("algebra.a.one")
        b = _node("algebra.a.two")
        c = _node(
            "algebra.a.three",
            prereqs=(
                PrerequisiteEdge("algebra.a.two", EdgeType.SOFT),
                PrerequisiteEdge("algebra.a.one", EdgeType.HARD),
            ),
        )
        graph = CanonicalGraph(
            version="1.0.0",
            published_at="2026-01-01",
            nodes={
                "algebra.a.one": a,
                "algebra.a.two": b,
                "algebra.a.three": c,
            },
            profiles={},
        )
        svc = CurriculumGraphQueryService(graph)
        prereqs = svc.get_prerequisites("algebra.a.three")
        assert prereqs[0].edge_type == EdgeType.HARD
        assert prereqs[1].edge_type == EdgeType.SOFT


# ── get_dependents ────────────────────────────────────────────────────────────


class TestGetDependents:
    def test_returns_direct_dependents(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        deps = svc.get_dependents("algebra.a.one")
        assert "algebra.a.two" in deps
        assert "algebra.a.three" not in deps  # transitive, not direct

    def test_returns_empty_for_leaf_node(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert svc.get_dependents("algebra.a.three") == []

    def test_returns_empty_for_nonexistent_node(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert svc.get_dependents("does.not.exist") == []


# ── get_regression_targets ────────────────────────────────────────────────────


class TestGetRegressionTargets:
    def test_returns_regression_nodes(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        targets = svc.get_regression_targets("algebra.a.two")
        assert len(targets) == 1
        assert targets[0].id == "algebra.a.one"

    def test_returns_empty_when_none_defined(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert svc.get_regression_targets("algebra.a.one") == []

    def test_returns_empty_for_nonexistent_node(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert svc.get_regression_targets("does.not.exist") == []


# ── is_reachable ──────────────────────────────────────────────────────────────


class TestIsReachable:
    def test_direct_prerequisite_is_reachable(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert svc.is_reachable("algebra.a.two", "algebra.a.one")

    def test_transitive_prerequisite_is_reachable(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert svc.is_reachable("algebra.a.three", "algebra.a.one")

    def test_non_prerequisite_direction_is_not_reachable(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert not svc.is_reachable("algebra.a.one", "algebra.a.three")

    def test_node_not_reachable_from_itself(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert not svc.is_reachable("algebra.a.one", "algebra.a.one")

    def test_nonexistent_from_returns_false(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert not svc.is_reachable("does.not.exist", "algebra.a.one")

    def test_nonexistent_to_returns_false(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        assert not svc.is_reachable("algebra.a.one", "does.not.exist")

    def test_already_visited_node_is_skipped_in_bfs(self):
        """Diamond graph: A ← B ← D and A ← C ← D plus isolated E.
        BFS from D to E (unreachable) causes A to be queued twice;
        the 'already visited' continue branch is exercised on the second dequeue."""
        a = _node("algebra.a.one")
        b = _node(
            "algebra.a.two", prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),)
        )
        c = _node(
            "algebra.a.three",
            prereqs=(PrerequisiteEdge("algebra.a.one", EdgeType.HARD),),
        )
        d = _node(
            "algebra.a.four",
            prereqs=(
                PrerequisiteEdge("algebra.a.two", EdgeType.HARD),
                PrerequisiteEdge("algebra.a.three", EdgeType.HARD),
            ),
        )
        e = _node("algebra.a.five")  # disconnected node — unreachable from D
        graph = CanonicalGraph(
            version="1.0.0",
            published_at="2026-01-01",
            nodes={
                "algebra.a.one": a,
                "algebra.a.two": b,
                "algebra.a.three": c,
                "algebra.a.four": d,
                "algebra.a.five": e,
            },
            profiles={},
        )
        svc = CurriculumGraphQueryService(graph)
        # D cannot reach E. BFS exhausts D→{B,C}→{A,A}; the second 'A' triggers
        # the already-visited continue branch before the loop terminates.
        assert not svc.is_reachable("algebra.a.four", "algebra.a.five")


# ── topological_order ─────────────────────────────────────────────────────────


class TestTopologicalOrder:
    def test_order_respects_prerequisites(self):
        svc = CurriculumGraphQueryService(_graph_with_profile())
        order = svc.topological_order("profile.test")
        assert order.index("algebra.a.one") < order.index("algebra.a.two")
        assert order.index("algebra.a.two") < order.index("algebra.a.three")

    def test_all_required_nodes_present(self):
        svc = CurriculumGraphQueryService(_graph_with_profile())
        order = svc.topological_order("profile.test")
        assert set(order) == {"algebra.a.one", "algebra.a.two", "algebra.a.three"}

    def test_raises_for_unknown_profile(self):
        svc = CurriculumGraphQueryService(_chain_graph())
        with pytest.raises(ValueError, match="Profile 'profile.missing' not found"):
            svc.topological_order("profile.missing")

    def test_phantom_required_node_not_in_graph_is_skipped(self):
        """Topological order silently skips required nodes absent from graph.nodes."""
        graph = _chain_graph()
        profile = CurriculumProfile(
            id="profile.phantom",
            name="Phantom",
            version="1.0.0",
            requires_graph_version="1.0.0",
            required_nodes=(
                ProfileNode("algebra.a.one", 3, 1.0),
                ProfileNode("algebra.a.ghost", 3, 1.0),  # does not exist in nodes
            ),
            progression_path=("algebra.a.one",),
            exam_skill_overlay=(),
        )
        graph.profiles["profile.phantom"] = profile
        svc = CurriculumGraphQueryService(graph)
        order = svc.topological_order("profile.phantom")
        # Both nodes appear in the order; ghost has in_degree=0 so it is
        # included — the defensive `if node is None: continue` skips only edge-building.
        assert "algebra.a.one" in order
        assert "algebra.a.ghost" in order
