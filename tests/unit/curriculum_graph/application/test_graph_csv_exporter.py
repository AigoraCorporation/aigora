from __future__ import annotations

import csv
from pathlib import Path

import pytest

from aigora.curriculum_graph.application.graph_csv_exporter import (
    GraphCsvExporter,
    GraphCsvExporterError,
)
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.node import Node


def make_mastery_scale() -> MasteryScale:
    return MasteryScale(
        criteria_by_level={
            MasteryLevel.RECOGNISES: MasteryCriterion(
                level=MasteryLevel.RECOGNISES,
                description="Recognises the concept.",
            ),
            MasteryLevel.INDEPENDENT: MasteryCriterion(
                level=MasteryLevel.INDEPENDENT,
                description="Solves independently.",
            ),
        }
    )


def make_node(node_id: str, name: str, domain: str) -> Node:
    return Node(
        id=node_id,
        name=name,
        domain=domain,
        description=f"{name} description.",
        mastery_criteria=make_mastery_scale(),
    )


def make_graph() -> CurriculumGraph:
    fractions_id = "math.arithmetic.fractions"
    equations_id = "math.algebra.linear-equations"

    fractions = make_node(fractions_id, "Fractions", "arithmetic")
    equations = make_node(equations_id, "Linear Equations", "algebra")

    edge = Edge(
        type=EdgeType.HARD_PREREQUISITE,
        source=fractions_id,
        target=equations_id,
    )

    profile = CurriculumProfile(
        id="profile.sat-math",
        name="SAT Math",
        required_nodes={fractions_id, equations_id},
        mastery_targets={
            fractions_id: MasteryLevel.INDEPENDENT,
            equations_id: MasteryLevel.EFFICIENT,
        },
        node_weights={
            fractions_id: 1.0,
            equations_id: 2.0,
        },
        progression_path=[fractions_id, equations_id],
    )

    return CurriculumGraph(
        nodes={
            equations_id: equations,
            fractions_id: fractions,
        },
        edges=[edge],
        profiles={
            profile.id: profile,
        },
        version="0.2.0",
    )


def read_csv(file_path: Path) -> list[dict[str, str]]:
    with file_path.open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def test_should_export_all_canonical_csv_files(tmp_path: Path):
    graph = make_graph()

    result = GraphCsvExporter().export(graph, tmp_path)

    expected_files = {
        "nodes.csv",
        "edges.csv",
        "profiles.csv",
        "profile_mastery_targets.csv",
        "profile_node_weights.csv",
        "profile_progression_paths.csv",
    }

    assert set(result.keys()) == expected_files

    for file_name in expected_files:
        assert (tmp_path / file_name).exists()


def test_should_export_nodes_csv(tmp_path: Path):
    graph = make_graph()

    GraphCsvExporter().export(graph, tmp_path)

    rows = read_csv(tmp_path / "nodes.csv")

    assert rows == [
        {
            "id": "math.algebra.linear-equations",
            "name": "Linear Equations",
            "domain": "algebra",
            "description": "Linear Equations description.",
        },
        {
            "id": "math.arithmetic.fractions",
            "name": "Fractions",
            "domain": "arithmetic",
            "description": "Fractions description.",
        },
    ]


def test_should_export_edges_csv(tmp_path: Path):
    graph = make_graph()

    GraphCsvExporter().export(graph, tmp_path)

    rows = read_csv(tmp_path / "edges.csv")

    assert rows == [
        {
            "type": "hard_prerequisite",
            "source": "math.arithmetic.fractions",
            "target": "math.algebra.linear-equations",
        }
    ]


def test_should_export_profiles_csv(tmp_path: Path):
    graph = make_graph()

    GraphCsvExporter().export(graph, tmp_path)

    rows = read_csv(tmp_path / "profiles.csv")

    assert rows == [
        {
            "id": "profile.sat-math",
            "name": "SAT Math",
        }
    ]


def test_should_export_profile_mastery_targets_csv(tmp_path: Path):
    graph = make_graph()

    GraphCsvExporter().export(graph, tmp_path)

    rows = read_csv(tmp_path / "profile_mastery_targets.csv")

    assert rows == [
        {
            "profile_id": "profile.sat-math",
            "node_id": "math.algebra.linear-equations",
            "mastery_level": "4",
        },
        {
            "profile_id": "profile.sat-math",
            "node_id": "math.arithmetic.fractions",
            "mastery_level": "3",
        },
    ]


def test_should_export_profile_node_weights_csv(tmp_path: Path):
    graph = make_graph()

    GraphCsvExporter().export(graph, tmp_path)

    rows = read_csv(tmp_path / "profile_node_weights.csv")

    assert rows == [
        {
            "profile_id": "profile.sat-math",
            "node_id": "math.algebra.linear-equations",
            "weight": "2.0",
        },
        {
            "profile_id": "profile.sat-math",
            "node_id": "math.arithmetic.fractions",
            "weight": "1.0",
        },
    ]


def test_should_export_profile_progression_paths_csv(tmp_path: Path):
    graph = make_graph()

    GraphCsvExporter().export(graph, tmp_path)

    rows = read_csv(tmp_path / "profile_progression_paths.csv")

    assert rows == [
        {
            "profile_id": "profile.sat-math",
            "position": "0",
            "node_id": "math.arithmetic.fractions",
        },
        {
            "profile_id": "profile.sat-math",
            "position": "1",
            "node_id": "math.algebra.linear-equations",
        },
    ]


def test_should_export_deterministic_output_across_runs(tmp_path: Path):
    graph = make_graph()
    exporter = GraphCsvExporter()

    exporter.export(graph, tmp_path)
    first_snapshot = {
        file_path.name: file_path.read_text(encoding="utf-8")
        for file_path in sorted(tmp_path.glob("*.csv"))
    }

    exporter.export(graph, tmp_path)
    second_snapshot = {
        file_path.name: file_path.read_text(encoding="utf-8")
        for file_path in sorted(tmp_path.glob("*.csv"))
    }

    assert first_snapshot == second_snapshot


def test_should_fail_when_output_path_is_file(tmp_path: Path):
    graph = make_graph()
    output_file = tmp_path / "output.csv"
    output_file.write_text("not a directory", encoding="utf-8")

    with pytest.raises(
        GraphCsvExporterError,
        match="Failed to export CurriculumGraph CSV files",
    ):
        GraphCsvExporter().export(graph, output_file)