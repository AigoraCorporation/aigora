"""
Unit tests for YAMLGraphLoader, covering error paths in metadata,
node, and profile loading.
"""
import pytest

from curriculum_graph.infrastructure.loaders.yaml_loader import (
    GraphLoadError,
    YAMLGraphLoader,
)


def _write_valid_metadata(graph_dir):
    (graph_dir / "metadata.yaml").write_text(
        "version: '1.0.0'\npublished_at: '2026-01-01'\n"
    )


# ── Metadata loading ──────────────────────────────────────────────────────────


class TestMetadataLoading:
    def test_raises_when_metadata_yaml_missing(self, tmp_path):
        """Graph dir exists but has no metadata.yaml → GraphLoadError."""
        graph_dir = tmp_path / "graph"
        graph_dir.mkdir()
        (graph_dir / "nodes").mkdir()
        with pytest.raises(GraphLoadError, match="metadata.yaml not found"):
            YAMLGraphLoader().load(graph_dir)

    def test_raises_when_metadata_has_no_version(self, tmp_path):
        """metadata.yaml without a 'version' key → GraphLoadError."""
        graph_dir = tmp_path / "graph"
        graph_dir.mkdir()
        (graph_dir / "metadata.yaml").write_text("published_at: '2026-01-01'\n")
        with pytest.raises(GraphLoadError, match="version"):
            YAMLGraphLoader().load(graph_dir)


# ── Node directory loading ────────────────────────────────────────────────────


class TestNodeDirLoading:
    def test_no_nodes_dir_returns_empty_node_set(self, tmp_path):
        """A graph dir without a nodes/ sub-directory loads fine with zero nodes."""
        graph_dir = tmp_path / "graph"
        graph_dir.mkdir()
        _write_valid_metadata(graph_dir)
        # Deliberately do NOT create a nodes/ directory.
        (graph_dir / "profiles").mkdir()
        graph = YAMLGraphLoader().load(graph_dir)
        assert graph.nodes == {}

    def test_raises_on_malformed_node_yaml(self, tmp_path):
        """A node YAML that is missing required keys raises GraphLoadError."""
        graph_dir = tmp_path / "graph"
        graph_dir.mkdir()
        _write_valid_metadata(graph_dir)
        nodes_dir = graph_dir / "nodes" / "algebra" / "a"
        nodes_dir.mkdir(parents=True)
        # Missing 'mastery_criteria' — will cause a KeyError inside _parse_node.
        (nodes_dir / "broken.yaml").write_text(
            "id: algebra.a.one\n"
            "name: Broken\n"
            "domain: algebra\n"
            "description: desc\n"
            "prerequisite_ids: []\n"
            "regression_ids: []\n"
        )
        with pytest.raises(GraphLoadError, match="Failed to parse node file"):
            YAMLGraphLoader().load(graph_dir)


# ── Profile directory loading ─────────────────────────────────────────────────


class TestProfileDirLoading:
    def test_no_profiles_dir_returns_empty_profile_set(self, tmp_path):
        """A graph dir without a profiles/ sub-directory loads fine with zero profiles."""
        graph_dir = tmp_path / "graph"
        graph_dir.mkdir()
        _write_valid_metadata(graph_dir)
        (graph_dir / "nodes").mkdir()
        # Deliberately do NOT create a profiles/ directory.
        graph = YAMLGraphLoader().load(graph_dir)
        assert graph.profiles == {}

    def test_raises_on_malformed_profile_yaml(self, tmp_path):
        """A profile YAML missing required keys raises GraphLoadError."""
        graph_dir = tmp_path / "graph"
        graph_dir.mkdir()
        _write_valid_metadata(graph_dir)
        (graph_dir / "nodes").mkdir()
        profiles_dir = graph_dir / "profiles"
        profiles_dir.mkdir()
        # Missing 'requires_graph_version' — will cause a KeyError inside _parse_profile.
        (profiles_dir / "profile.broken.yaml").write_text(
            "id: profile.broken\n"
            "name: Broken Profile\n"
            "version: '1.0.0'\n"
            "required_nodes: []\n"
            "progression_path: []\n"
        )
        with pytest.raises(GraphLoadError, match="Failed to parse profile file"):
            YAMLGraphLoader().load(graph_dir)
