from __future__ import annotations

import json
from pathlib import Path

import yaml

from aigora.curriculum_graph.application.use_cases.export_graph import CurriculumGraphExportFormat
from aigora.curriculum_graph.infrastructure.files.exporters import (
    CurriculumGraphJsonExporter,
    CurriculumGraphYamlExporter,
    build_file_curriculum_graph_exporter_registry,
)
from tests.unit.curriculum_graph.infrastructure.files.csv.test_graph_csv_exporter import (
    make_graph,
)


def test_should_export_graph_as_json(tmp_path: Path):
    graph = make_graph()

    result = CurriculumGraphJsonExporter().export(graph, tmp_path)

    assert result == {"graph.json": tmp_path / "graph.json"}
    payload = json.loads((tmp_path / "graph.json").read_text(encoding="utf-8"))
    assert payload["version"] == "0.2.0"
    assert len(payload["nodes"]) == 2
    assert len(payload["edges"]) == 1
    assert len(payload["profiles"]) == 1


def test_should_export_graph_as_yaml(tmp_path: Path):
    graph = make_graph()

    result = CurriculumGraphYamlExporter().export(graph, tmp_path)

    assert result == {"graph.yaml": tmp_path / "graph.yaml"}
    payload = yaml.safe_load((tmp_path / "graph.yaml").read_text(encoding="utf-8"))
    assert payload["version"] == "0.2.0"
    assert len(payload["nodes"]) == 2
    assert len(payload["edges"]) == 1
    assert len(payload["profiles"]) == 1


def test_should_build_registry_with_csv_json_and_yaml_exporters(tmp_path: Path):
    graph = make_graph()
    registry = build_file_curriculum_graph_exporter_registry()

    registry.get(CurriculumGraphExportFormat.CSV).export(graph, tmp_path / "csv")
    registry.get(CurriculumGraphExportFormat.JSON).export(graph, tmp_path / "json")
    registry.get(CurriculumGraphExportFormat.YAML).export(graph, tmp_path / "yaml")

    assert (tmp_path / "csv" / "nodes.csv").exists()
    assert (tmp_path / "json" / "graph.json").exists()
    assert (tmp_path / "yaml" / "graph.yaml").exists()
