from __future__ import annotations

from pathlib import Path

import pytest

from aigora.curriculum_graph.application.loading.graph_loader import GraphLoader
from aigora.curriculum_graph.application.loading.loader_errors import GraphLoaderError
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel

_EXAMPLES_DIR = Path(__file__).parents[3] / "examples" / "curriculum_graph"

FRACTIONS_ID = "math.arithmetic.fractions"
EQUATIONS_ID = "math.algebra.linear-equations"
SAT_MATH_PROFILE_ID = "profile.sat-math"


@pytest.fixture(scope="module")
def loader() -> GraphLoader:
    return GraphLoader()


@pytest.fixture(scope="module")
def canonical_yaml_graph(loader: GraphLoader) -> CurriculumGraph:
    return loader.load(_EXAMPLES_DIR / "canonical" / "graph.yaml")


@pytest.fixture(scope="module")
def canonical_json_graph(loader: GraphLoader) -> CurriculumGraph:
    return loader.load(_EXAMPLES_DIR / "canonical" / "graph.json")


# ── Happy path ────────────────────────────────────────────────────────────────


def test_should_load_valid_yaml_graph_successfully(
    canonical_yaml_graph: CurriculumGraph,
):
    assert isinstance(canonical_yaml_graph, CurriculumGraph)
    assert canonical_yaml_graph.version == "0.2.0"
    assert len(canonical_yaml_graph.nodes) == 2
    assert len(canonical_yaml_graph.edges) == 1
    assert len(canonical_yaml_graph.profiles) == 1


def test_should_load_valid_json_graph_successfully(
    canonical_json_graph: CurriculumGraph,
):
    assert isinstance(canonical_json_graph, CurriculumGraph)
    assert canonical_json_graph.version == "0.2.0"
    assert len(canonical_json_graph.nodes) == 2
    assert len(canonical_json_graph.edges) == 1
    assert len(canonical_json_graph.profiles) == 1


def test_should_load_equivalent_yaml_and_json_graphs(
    canonical_yaml_graph: CurriculumGraph,
    canonical_json_graph: CurriculumGraph,
):
    assert canonical_yaml_graph.version == canonical_json_graph.version
    assert set(canonical_yaml_graph.nodes.keys()) == set(canonical_json_graph.nodes.keys())
    assert len(canonical_yaml_graph.edges) == len(canonical_json_graph.edges)
    assert set(canonical_yaml_graph.profiles.keys()) == set(
        canonical_json_graph.profiles.keys()
    )


# ── Node assembly ─────────────────────────────────────────────────────────────


def test_should_assemble_nodes_with_correct_ids(canonical_yaml_graph: CurriculumGraph):
    assert FRACTIONS_ID in canonical_yaml_graph.nodes
    assert EQUATIONS_ID in canonical_yaml_graph.nodes


def test_should_assemble_node_with_correct_fields(canonical_yaml_graph: CurriculumGraph):
    node = canonical_yaml_graph.nodes[FRACTIONS_ID]

    assert node.name == "Fractions"
    assert node.domain == "arithmetic"
    assert "fraction" in node.description.lower()


def test_should_assemble_node_with_correct_mastery_criteria(
    canonical_yaml_graph: CurriculumGraph,
):
    node = canonical_yaml_graph.nodes[FRACTIONS_ID]

    assert node.mastery_criteria.has_level(MasteryLevel.RECOGNISES)
    assert node.mastery_criteria.has_level(MasteryLevel.INDEPENDENT)

    criterion = node.mastery_criteria.get(MasteryLevel.RECOGNISES)
    assert criterion.description == "Recognises fractions in simple contexts."


def test_should_assemble_node_with_correct_prerequisite_ids(
    canonical_yaml_graph: CurriculumGraph,
):
    equations = canonical_yaml_graph.nodes[EQUATIONS_ID]

    assert FRACTIONS_ID in equations.prerequisite_ids


# ── Edge assembly ─────────────────────────────────────────────────────────────


def test_should_assemble_edge_with_correct_type_and_endpoints(
    canonical_yaml_graph: CurriculumGraph,
):
    edge = canonical_yaml_graph.edges[0]

    assert edge.type == EdgeType.HARD_PREREQUISITE
    assert edge.source == FRACTIONS_ID
    assert edge.target == EQUATIONS_ID


def test_should_resolve_outgoing_edges_from_assembled_graph(
    canonical_yaml_graph: CurriculumGraph,
):
    outgoing = canonical_yaml_graph.outgoing_edges(FRACTIONS_ID)

    assert len(outgoing) == 1
    assert outgoing[0].target == EQUATIONS_ID


def test_should_resolve_incoming_edges_from_assembled_graph(
    canonical_yaml_graph: CurriculumGraph,
):
    incoming = canonical_yaml_graph.incoming_edges(EQUATIONS_ID)

    assert len(incoming) == 1
    assert incoming[0].source == FRACTIONS_ID


# ── Profile assembly ──────────────────────────────────────────────────────────


def test_should_assemble_profile_with_correct_id_and_name(
    canonical_yaml_graph: CurriculumGraph,
):
    assert SAT_MATH_PROFILE_ID in canonical_yaml_graph.profiles

    profile = canonical_yaml_graph.profiles[SAT_MATH_PROFILE_ID]
    assert profile.name == "SAT Math"


def test_should_assemble_profile_with_correct_required_nodes(
    canonical_yaml_graph: CurriculumGraph,
):
    profile = canonical_yaml_graph.profiles[SAT_MATH_PROFILE_ID]

    assert FRACTIONS_ID in profile.required_nodes
    assert EQUATIONS_ID in profile.required_nodes


def test_should_assemble_profile_with_correct_mastery_targets(
    canonical_yaml_graph: CurriculumGraph,
):
    profile = canonical_yaml_graph.profiles[SAT_MATH_PROFILE_ID]

    assert profile.mastery_targets[FRACTIONS_ID] == MasteryLevel.INDEPENDENT
    assert profile.mastery_targets[EQUATIONS_ID] == MasteryLevel.EFFICIENT


def test_should_assemble_profile_with_correct_node_weights(
    canonical_yaml_graph: CurriculumGraph,
):
    profile = canonical_yaml_graph.profiles[SAT_MATH_PROFILE_ID]

    assert profile.node_weights[FRACTIONS_ID] == pytest.approx(1.0)
    assert profile.node_weights[EQUATIONS_ID] == pytest.approx(2.0)


def test_should_assemble_profile_with_correct_progression_path(
    canonical_yaml_graph: CurriculumGraph,
):
    profile = canonical_yaml_graph.profiles[SAT_MATH_PROFILE_ID]

    assert profile.progression_path == [FRACTIONS_ID, EQUATIONS_ID]


# ── Parser / schema failures ──────────────────────────────────────────────────


def test_should_fail_loading_when_file_extension_is_not_supported(tmp_path: Path):
    file_path = tmp_path / "graph.txt"
    file_path.write_text("invalid content", encoding="utf-8")

    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(file_path)


def test_should_fail_loading_when_yaml_is_malformed():
    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(_EXAMPLES_DIR / "invalid" / "malformed.yaml")


def test_should_fail_loading_when_required_nodes_key_is_missing():
    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(_EXAMPLES_DIR / "invalid" / "missing_nodes.json")


# ── Version validation failures ───────────────────────────────────────────────


def test_should_fail_loading_when_version_is_missing(tmp_path: Path):
    file_path = tmp_path / "missing_version.yaml"
    file_path.write_text(
        """
nodes: []
edges: []
profiles: []
""",
        encoding="utf-8",
    )

    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(file_path)


def test_should_fail_loading_when_version_is_not_string(tmp_path: Path):
    file_path = tmp_path / "invalid_version.yaml"
    file_path.write_text(
        """
version: 1
nodes: []
edges: []
profiles: []
""",
        encoding="utf-8",
    )

    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(file_path)


def test_should_fail_loading_when_version_format_is_invalid(tmp_path: Path):
    file_path = tmp_path / "invalid_version_format.yaml"
    file_path.write_text(
        """
version: invalid-version
nodes: []
edges: []
profiles: []
""",
        encoding="utf-8",
    )

    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(file_path)


# ── Domain validation failures ────────────────────────────────────────────────


def test_should_fail_loading_when_graph_has_cyclic_prerequisites(tmp_path: Path):
    file_path = tmp_path / "cyclic_graph.yaml"
    file_path.write_text(
        """
version: "0.2.0"

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

    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(file_path)


def test_should_fail_loading_when_edge_references_unknown_node(tmp_path: Path):
    file_path = tmp_path / "invalid_edge_reference.yaml"
    file_path.write_text(
        """
version: "0.2.0"

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

    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(file_path)


def test_should_fail_loading_when_profile_references_unknown_node(tmp_path: Path):
    file_path = tmp_path / "invalid_profile_reference.yaml"
    file_path.write_text(
        """
version: "0.2.0"

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

    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(file_path)


def test_should_fail_loading_when_profile_uses_unexposed_as_target(tmp_path: Path):
    file_path = tmp_path / "invalid_profile_mastery_target.yaml"
    file_path.write_text(
        """
version: "0.2.0"

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

    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(file_path)


def test_should_fail_loading_when_profile_weight_is_zero(tmp_path: Path):
    file_path = tmp_path / "invalid_profile_weight.yaml"
    file_path.write_text(
        """
version: "0.2.0"

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

    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(file_path)


def test_should_fail_loading_when_progression_path_violates_prerequisite_order(
    tmp_path: Path,
):
    file_path = tmp_path / "invalid_progression_path.yaml"
    file_path.write_text(
        """
version: "0.2.0"

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

    with pytest.raises(GraphLoaderError, match="Failed to load CurriculumGraph"):
        GraphLoader().load(file_path)