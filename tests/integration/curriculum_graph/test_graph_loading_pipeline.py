from __future__ import annotations

from pathlib import Path

import pytest

from aigora.curriculum_graph.application.graph_loader import GraphLoader
from aigora.curriculum_graph.application.loader_errors import GraphLoaderError
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph

_EXAMPLES_DIR = Path(__file__).parents[3] / "examples" / "curriculum_graph"


# ── Happy path ────────────────────────────────────────────────────────────────


def test_should_load_valid_yaml_graph_successfully():
    loader = GraphLoader()

    graph = loader.load(_EXAMPLES_DIR / "canonical" / "graph.yaml")

    assert isinstance(graph, CurriculumGraph)
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert len(graph.profiles) == 1


def test_should_load_valid_json_graph_successfully():
    loader = GraphLoader()

    graph = loader.load(_EXAMPLES_DIR / "canonical" / "graph.json")

    assert isinstance(graph, CurriculumGraph)
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1
    assert len(graph.profiles) == 1


def test_should_load_equivalent_yaml_and_json_graphs():
    loader = GraphLoader()

    yaml_graph = loader.load(_EXAMPLES_DIR / "canonical" / "graph.yaml")
    json_graph = loader.load(_EXAMPLES_DIR / "canonical" / "graph.json")

    assert set(yaml_graph.nodes.keys()) == set(json_graph.nodes.keys())
    assert len(yaml_graph.edges) == len(json_graph.edges)
    assert set(yaml_graph.profiles.keys()) == set(json_graph.profiles.keys())


# ── Parsing / structure failures ──────────────────────────────────────────────


def test_should_fail_loading_when_file_extension_is_not_supported(tmp_path: Path):
    file_path = tmp_path / "graph.txt"
    file_path.write_text("invalid content", encoding="utf-8")

    loader = GraphLoader()

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file",
    ):
        loader.load(file_path)


def test_should_fail_loading_when_yaml_is_malformed():
    loader = GraphLoader()

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file",
    ):
        loader.load(_EXAMPLES_DIR / "invalid" / "malformed.yaml")


def test_should_fail_loading_when_required_nodes_key_is_missing():
    loader = GraphLoader()

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file",
    ):
        loader.load(_EXAMPLES_DIR / "invalid" / "missing_nodes.json")


# ── Validation failures ───────────────────────────────────────────────────────


def test_should_fail_loading_when_graph_has_cyclic_prerequisites(tmp_path: Path):
    file_path = tmp_path / "cyclic_graph.yaml"
    file_path.write_text(
        """
nodes:
  - id: math.arithmetic.fractions
    name: Fractions
    domain: mathematics
    description: Understand basic fractions.
    mastery:
      levels:
        - level: 1
          description: Recognises fractions.
        - level: 3
          description: Solves fraction problems independently.

  - id: math.algebra.linear-equations
    name: Linear Equations
    domain: mathematics
    description: Solve simple linear equations.
    mastery:
      levels:
        - level: 2
          description: Solves equations with guidance.
        - level: 4
          description: Solves equations efficiently.

edges:
  - type: hard_prerequisite
    source: math.arithmetic.fractions
    target: math.algebra.linear-equations

  - type: hard_prerequisite
    source: math.algebra.linear-equations
    target: math.arithmetic.fractions

profiles:
  - id: profile.sat-math
    name: SAT Math
    required_nodes:
      - math.arithmetic.fractions
      - math.algebra.linear-equations
    mastery_targets:
      math.arithmetic.fractions: 3
      math.algebra.linear-equations: 4
    node_weights:
      math.arithmetic.fractions: 1.0
      math.algebra.linear-equations: 1.0
    progression_path:
      - math.arithmetic.fractions
      - math.algebra.linear-equations
""",
        encoding="utf-8",
    )

    loader = GraphLoader()

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file",
    ):
        loader.load(file_path)


def test_should_fail_loading_when_edge_references_unknown_node(tmp_path: Path):
    file_path = tmp_path / "invalid_edge_reference.yaml"
    file_path.write_text(
        """
nodes:
  - id: math.arithmetic.fractions
    name: Fractions
    domain: mathematics
    description: Understand basic fractions.
    mastery:
      levels:
        - level: 1
          description: Recognises fractions.

edges:
  - type: hard_prerequisite
    source: math.arithmetic.fractions
    target: math.algebra.linear-equations

profiles: []
""",
        encoding="utf-8",
    )

    loader = GraphLoader()

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file",
    ):
        loader.load(file_path)


def test_should_fail_loading_when_profile_references_unknown_node(tmp_path: Path):
    file_path = tmp_path / "invalid_profile_reference.yaml"
    file_path.write_text(
        """
nodes:
  - id: math.arithmetic.fractions
    name: Fractions
    domain: mathematics
    description: Understand basic fractions.
    mastery:
      levels:
        - level: 1
          description: Recognises fractions.

edges: []

profiles:
  - id: profile.sat-math
    name: SAT Math
    required_nodes:
      - math.arithmetic.fractions
      - math.algebra.linear-equations
    mastery_targets:
      math.arithmetic.fractions: 1
    node_weights:
      math.arithmetic.fractions: 1.0
    progression_path:
      - math.arithmetic.fractions
""",
        encoding="utf-8",
    )

    loader = GraphLoader()

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file",
    ):
        loader.load(file_path)


def test_should_fail_loading_when_profile_uses_unexposed_as_target(tmp_path: Path):
    file_path = tmp_path / "invalid_profile_mastery_target.yaml"
    file_path.write_text(
        """
nodes:
  - id: math.arithmetic.fractions
    name: Fractions
    domain: mathematics
    description: Understand basic fractions.
    mastery:
      levels:
        - level: 1
          description: Recognises fractions.

edges: []

profiles:
  - id: profile.sat-math
    name: SAT Math
    required_nodes:
      - math.arithmetic.fractions
    mastery_targets:
      math.arithmetic.fractions: 0
    node_weights:
      math.arithmetic.fractions: 1.0
    progression_path:
      - math.arithmetic.fractions
""",
        encoding="utf-8",
    )

    loader = GraphLoader()

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file",
    ):
        loader.load(file_path)


def test_should_fail_loading_when_profile_weight_is_zero(tmp_path: Path):
    file_path = tmp_path / "invalid_profile_weight.yaml"
    file_path.write_text(
        """
nodes:
  - id: math.arithmetic.fractions
    name: Fractions
    domain: mathematics
    description: Understand basic fractions.
    mastery:
      levels:
        - level: 1
          description: Recognises fractions.

edges: []

profiles:
  - id: profile.sat-math
    name: SAT Math
    required_nodes:
      - math.arithmetic.fractions
    mastery_targets:
      math.arithmetic.fractions: 1
    node_weights:
      math.arithmetic.fractions: 0.0
    progression_path:
      - math.arithmetic.fractions
""",
        encoding="utf-8",
    )

    loader = GraphLoader()

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file",
    ):
        loader.load(file_path)


def test_should_fail_loading_when_progression_path_violates_prerequisite_order(
    tmp_path: Path,
):
    file_path = tmp_path / "invalid_progression_path.yaml"
    file_path.write_text(
        """
nodes:
  - id: math.arithmetic.fractions
    name: Fractions
    domain: mathematics
    description: Understand basic fractions.
    mastery:
      levels:
        - level: 1
          description: Recognises fractions.

  - id: math.algebra.linear-equations
    name: Linear Equations
    domain: mathematics
    description: Solve simple linear equations.
    mastery:
      levels:
        - level: 2
          description: Solves equations with guidance.

edges:
  - type: hard_prerequisite
    source: math.arithmetic.fractions
    target: math.algebra.linear-equations

profiles:
  - id: profile.sat-math
    name: SAT Math
    required_nodes:
      - math.arithmetic.fractions
      - math.algebra.linear-equations
    mastery_targets:
      math.arithmetic.fractions: 1
      math.algebra.linear-equations: 2
    node_weights:
      math.arithmetic.fractions: 1.0
      math.algebra.linear-equations: 1.0
    progression_path:
      - math.algebra.linear-equations
      - math.arithmetic.fractions
""",
        encoding="utf-8",
    )

    loader = GraphLoader()

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file",
    ):
        loader.load(file_path)