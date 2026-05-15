from __future__ import annotations

from pathlib import Path

import pytest

from aigora.curriculum_graph.application.use_cases.export_graph import (
    CurriculumGraphExportFormat,
    CurriculumGraphExporterRegistry,
)
from aigora.curriculum_graph.application.use_cases.load_graph import LoadGraphResult
from aigora.curriculum_graph.application.use_cases.publish_graph import (
    PublishGraphCommand,
    PublishGraphUseCase,
)
from tests.unit.curriculum_graph.infrastructure.files.csv.test_graph_csv_exporter import (
    make_graph,
)


class SpyLoader:
    def __init__(self, graph) -> None:
        self.graph = graph
        self.received_command = None

    def execute(self, command):
        self.received_command = command
        return LoadGraphResult(
            graph=self.graph,
            nodes_loaded=len(self.graph.nodes),
            edges_loaded=len(self.graph.edges),
            profiles_loaded=len(self.graph.profiles),
            version=str(self.graph.version),
        )


class SpyRepository:
    def __init__(self) -> None:
        self.calls = []

    def apply_schema(self) -> None:
        self.calls.append("apply_schema")

    def persist(self, graph) -> None:
        self.calls.append(("persist", graph))

    def validate(self, graph) -> None:
        self.calls.append(("validate", graph))


class SpyExporter:
    def __init__(self) -> None:
        self.received_graph = None
        self.received_output_dir = None

    def export(self, graph, output_dir):
        self.received_graph = graph
        self.received_output_dir = Path(output_dir)
        return {"graph.json": Path(output_dir) / "graph.json"}


def test_publish_graph_should_load_persist_validate_and_return_summary():
    graph = make_graph()
    loader = SpyLoader(graph)
    repository = SpyRepository()

    result = PublishGraphUseCase(loader=loader, repository=repository).execute(
        PublishGraphCommand(file_path="curriculum.yaml")
    )

    assert loader.received_command.file_path == "curriculum.yaml"
    assert repository.calls == [
        "apply_schema",
        ("persist", graph),
        ("validate", graph),
    ]
    assert result.graph_version == str(graph.version)
    assert result.nodes_published == len(graph.nodes)
    assert result.edges_published == len(graph.edges)
    assert result.profiles_published == len(graph.profiles)
    assert result.graph_exported is False
    assert result.export_format is None
    assert result.exported_files == {}


def test_publish_graph_should_export_when_requested(tmp_path: Path):
    graph = make_graph()
    exporter = SpyExporter()
    registry = CurriculumGraphExporterRegistry({CurriculumGraphExportFormat.JSON: exporter})

    result = PublishGraphUseCase(
        loader=SpyLoader(graph),
        repository=SpyRepository(),
        exporter_registry=registry,
    ).execute(
        PublishGraphCommand(
            file_path="curriculum.yaml",
            export_graph=True,
            export_output_dir=tmp_path,
            export_format="json",
        )
    )

    assert exporter.received_graph is graph
    assert exporter.received_output_dir == tmp_path
    assert result.graph_exported is True
    assert result.export_format is CurriculumGraphExportFormat.JSON
    assert result.exported_files == {"graph.json": tmp_path / "graph.json"}


def test_publish_graph_should_require_registry_when_export_is_enabled():
    with pytest.raises(ValueError, match="requires an exporter registry"):
        PublishGraphUseCase(loader=SpyLoader(make_graph()), repository=SpyRepository()).execute(
            PublishGraphCommand(
                file_path="curriculum.yaml",
                export_graph=True,
                export_output_dir="out",
            )
        )


def test_publish_graph_should_require_output_dir_when_export_is_enabled():
    registry = CurriculumGraphExporterRegistry({"csv": SpyExporter()})

    with pytest.raises(ValueError, match="export_output_dir must be provided"):
        PublishGraphUseCase(
            loader=SpyLoader(make_graph()),
            repository=SpyRepository(),
            exporter_registry=registry,
        ).execute(
            PublishGraphCommand(
                file_path="curriculum.yaml",
                export_graph=True,
            )
        )


def test_publish_graph_command_should_normalize_yml_export_format():
    command = PublishGraphCommand(file_path="graph.yaml", export_format="yml")

    assert command.normalized_export_format() is CurriculumGraphExportFormat.YAML
