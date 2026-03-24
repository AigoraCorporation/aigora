from pathlib import Path

import pytest

from curriculum_graph.domain.enums import EdgeType, NodeStatus
from curriculum_graph.infrastructure.repositories.file_repository import (
    FileBasedCurriculumGraphRepository,
    GraphValidationError,
)
from curriculum_graph.infrastructure.loaders.yaml_loader import GraphLoadError

FIXTURES_GRAPH = Path(__file__).parent.parent / "fixtures" / "graph"


# ── Fixture ───────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def repo() -> FileBasedCurriculumGraphRepository:
    return FileBasedCurriculumGraphRepository(FIXTURES_GRAPH)


# ── Loading ───────────────────────────────────────────────────────────────────


class TestLoading:
    def test_loads_without_error(self, repo):
        assert repo is not None

    def test_raises_on_nonexistent_directory(self, tmp_path):
        with pytest.raises(GraphLoadError):
            FileBasedCurriculumGraphRepository(tmp_path / "nonexistent")

    def test_empty_graph_dir_loads_without_error(self, tmp_path):
        # A graph dir with metadata but no nodes/profiles — structurally valid.
        graph_dir = tmp_path / "graph"
        (graph_dir / "nodes").mkdir(parents=True)
        (graph_dir / "profiles").mkdir(parents=True)
        (graph_dir / "metadata.yaml").write_text("version: '1.0.0'\npublished_at: '2026-01-01'\n")
        repo = FileBasedCurriculumGraphRepository(graph_dir)
        assert repo is not None

    def test_raises_graph_validation_error_for_invalid_node_id(self, tmp_path):
        graph_dir = tmp_path / "graph"
        nodes_dir = graph_dir / "nodes" / "algebra" / "a"
        nodes_dir.mkdir(parents=True)
        (graph_dir / "profiles").mkdir(parents=True)
        (graph_dir / "metadata.yaml").write_text("version: '1.0.0'\npublished_at: '2026-01-01'\n")
        # Node file with an id that violates S2 (uppercase segment)
        (nodes_dir / "bad.yaml").write_text(
            "id: Algebra.a.bad\n"
            "name: Bad\n"
            "domain: algebra\n"
            "description: Desc\n"
            "mastery_criteria:\n"
            "  '1': L1\n  '2': L2\n  '3': L3\n  '4': L4\n  '5': L5\n"
            "error_taxonomy:\n"
            "  - name: E\n    description: A specific misconception.\n"
            "prerequisite_ids: []\n"
            "regression_ids: []\n"
        )
        with pytest.raises(GraphValidationError) as exc_info:
            FileBasedCurriculumGraphRepository(graph_dir)
        assert exc_info.value.report.has_errors
        assert "S2" in str(exc_info.value)


# ── get_node ──────────────────────────────────────────────────────────────────


class TestGetNode:
    def test_returns_foundational_node(self, repo):
        node = repo.get_node("algebra.arithmetic.integer-operations")
        assert node is not None
        assert node.id == "algebra.arithmetic.integer-operations"
        assert node.name == "Integer Operations"
        assert node.domain == "algebra"
        assert node.status == NodeStatus.ACTIVE

    def test_mastery_criteria_loaded(self, repo):
        node = repo.get_node("algebra.arithmetic.integer-operations")
        assert "number line" in node.mastery_criteria.level_1.lower()

    def test_error_taxonomy_loaded(self, repo):
        node = repo.get_node("algebra.arithmetic.integer-operations")
        assert len(node.error_taxonomy) >= 2

    def test_returns_none_for_unknown_id(self, repo):
        assert repo.get_node("does.not.exist") is None


# ── get_prerequisites ─────────────────────────────────────────────────────────


class TestGetPrerequisites:
    def test_foundational_node_has_no_prerequisites(self, repo):
        prereqs = repo.get_prerequisites("algebra.arithmetic.integer-operations")
        assert prereqs == []

    def test_node_with_hard_prerequisite(self, repo):
        prereqs = repo.get_prerequisites("algebra.arithmetic.fractions")
        assert len(prereqs) == 1
        assert prereqs[0].node_id == "algebra.arithmetic.integer-operations"
        assert prereqs[0].edge_type == EdgeType.HARD

    def test_node_with_mixed_prerequisites(self, repo):
        prereqs = repo.get_prerequisites("algebra.equations.linear-one-variable")
        edge_types = {e.edge_type for e in prereqs}
        assert EdgeType.HARD in edge_types
        assert EdgeType.SOFT in edge_types

    def test_hard_before_soft_in_result(self, repo):
        prereqs = repo.get_prerequisites("algebra.equations.linear-one-variable")
        hard_indices = [i for i, e in enumerate(prereqs) if e.edge_type == EdgeType.HARD]
        soft_indices = [i for i, e in enumerate(prereqs) if e.edge_type == EdgeType.SOFT]
        assert max(hard_indices) < min(soft_indices)


# ── get_dependents ────────────────────────────────────────────────────────────


class TestGetDependents:
    def test_foundational_node_has_dependents(self, repo):
        deps = repo.get_dependents("algebra.arithmetic.integer-operations")
        assert "algebra.arithmetic.fractions" in deps
        assert "algebra.equations.linear-one-variable" in deps

    def test_leaf_node_has_no_dependents(self, repo):
        deps = repo.get_dependents("algebra.equations.linear-one-variable")
        assert deps == []


# ── get_regression_targets ────────────────────────────────────────────────────


class TestGetRegressionTargets:
    def test_returns_regression_targets(self, repo):
        targets = repo.get_regression_targets("algebra.arithmetic.fractions")
        target_ids = [t.id for t in targets]
        assert "algebra.arithmetic.integer-operations" in target_ids

    def test_foundational_node_has_no_regressions(self, repo):
        targets = repo.get_regression_targets("algebra.arithmetic.integer-operations")
        assert targets == []


# ── is_reachable ──────────────────────────────────────────────────────────────


class TestIsReachable:
    def test_direct_hard_prerequisite_is_reachable(self, repo):
        assert repo.is_reachable(
            "algebra.arithmetic.fractions",
            "algebra.arithmetic.integer-operations",
        )

    def test_transitive_prerequisite_is_reachable(self, repo):
        # linear-one-variable → fractions (soft) → integer-operations (hard)
        assert repo.is_reachable(
            "algebra.equations.linear-one-variable",
            "algebra.arithmetic.integer-operations",
        )

    def test_downstream_direction_is_not_reachable(self, repo):
        assert not repo.is_reachable(
            "algebra.arithmetic.integer-operations",
            "algebra.equations.linear-one-variable",
        )


# ── get_profile ───────────────────────────────────────────────────────────────


class TestGetProfile:
    def test_returns_fuvest_profile(self, repo):
        profile = repo.get_profile("profile.fuvest")
        assert profile is not None
        assert profile.name == "Fuvest"
        assert profile.version == "1.0.0"
        assert profile.requires_graph_version == "1.0.0"

    def test_profile_required_nodes_loaded(self, repo):
        profile = repo.get_profile("profile.fuvest")
        ids = profile.required_node_ids()
        assert "algebra.arithmetic.integer-operations" in ids
        assert "algebra.equations.linear-one-variable" in ids

    def test_profile_mastery_targets_loaded(self, repo):
        profile = repo.get_profile("profile.fuvest")
        assert profile.mastery_target_for("algebra.equations.linear-one-variable") == 4

    def test_profile_weights_loaded(self, repo):
        profile = repo.get_profile("profile.fuvest")
        assert profile.weight_for("algebra.equations.linear-one-variable") == 1.5

    def test_profile_exam_skill_overlay_loaded(self, repo):
        profile = repo.get_profile("profile.fuvest")
        assert len(profile.exam_skill_overlay) >= 1

    def test_returns_none_for_unknown_profile(self, repo):
        assert repo.get_profile("profile.missing") is None


# ── topological_order ─────────────────────────────────────────────────────────


class TestTopologicalOrder:
    def test_order_respects_hard_prerequisites(self, repo):
        order = repo.topological_order("profile.fuvest")
        assert order.index("algebra.arithmetic.integer-operations") < order.index(
            "algebra.equations.linear-one-variable"
        )
        assert order.index("algebra.arithmetic.integer-operations") < order.index(
            "algebra.arithmetic.fractions"
        )

    def test_all_required_nodes_in_order(self, repo):
        profile = repo.get_profile("profile.fuvest")
        order = repo.topological_order("profile.fuvest")
        assert set(order) == profile.required_node_ids()

    def test_raises_for_unknown_profile(self, repo):
        with pytest.raises(ValueError):
            repo.topological_order("profile.unknown")
