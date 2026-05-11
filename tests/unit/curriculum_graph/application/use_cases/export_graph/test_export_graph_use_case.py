from __future__ import annotations

from pathlib import Path

import pytest

from aigora.curriculum_graph.application.errors.export_graph_errors import (
    UnsupportedCurriculumGraphExportFormatError,
)
from aigora.curriculum_graph.application.use_cases.export_graph import (
    CurriculumGraphExportFormat,
    CurriculumGraphExporterRegistry,
    ExportGraphCommand,
    ExportGraphUseCase,
)
from tests.unit.curriculum_graph.infrastructure.files.csv.test_graph_csv_exporter import (
    make_graph,
)


class SpyExporter:
    def __init__(self) -> None:
        self.received_graph = None
        self.received_output_dir = None

    def export(self, graph, output_dir: str | Path) -> dict[str, Path]:
        self.received_graph = graph
        self.received_output_dir = Path(output_dir)
        return {"graph.spy": Path(output_dir) / "graph.spy"}


def test_export_graph_use_case_should_execute_selected_export_strategy(tmp_path: Path):
    graph = make_graph()
    exporter = SpyExporter()
    registry = CurriculumGraphExporterRegistry({CurriculumGraphExportFormat.JSON: exporter})

    result = ExportGraphUseCase(registry).execute(
        ExportGraphCommand(
            graph=graph,
            output_dir=tmp_path,
            output_format="json",
        )
    )

    assert exporter.received_graph is graph
    assert exporter.received_output_dir == tmp_path
    assert result.output_dir == tmp_path
    assert result.output_format is CurriculumGraphExportFormat.JSON
    assert result.exported_files == {"graph.spy": tmp_path / "graph.spy"}
    assert result.nodes_exported == len(graph.nodes)
    assert result.edges_exported == len(graph.edges)
    assert result.profiles_exported == len(graph.profiles)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (CurriculumGraphExportFormat.CSV, CurriculumGraphExportFormat.CSV),
        ("csv", CurriculumGraphExportFormat.CSV),
        (" JSON ", CurriculumGraphExportFormat.JSON),
        ("yml", CurriculumGraphExportFormat.YAML),
        ("yaml", CurriculumGraphExportFormat.YAML),
    ],
)
def test_export_format_should_normalize_supported_values(raw, expected):
    assert CurriculumGraphExportFormat.from_value(raw) is expected


def test_export_format_should_reject_unsupported_value():
    with pytest.raises(ValueError, match="Unsupported graph export format"):
        CurriculumGraphExportFormat.from_value("xml")


def test_registry_should_raise_when_format_is_not_registered():
    registry = CurriculumGraphExporterRegistry({"csv": SpyExporter()})

    with pytest.raises(
        UnsupportedCurriculumGraphExportFormatError,
        match="Supported formats: csv",
    ):
        registry.get("json")


def test_registry_should_raise_when_format_value_is_invalid():
    registry = CurriculumGraphExporterRegistry({"csv": SpyExporter()})

    with pytest.raises(
        UnsupportedCurriculumGraphExportFormatError,
        match="Unsupported graph export format",
    ):
        registry.get("xml")


def test_registry_error_should_report_none_when_no_formats_are_registered():
    registry = CurriculumGraphExporterRegistry({})

    with pytest.raises(
        UnsupportedCurriculumGraphExportFormatError,
        match="Supported formats: none",
    ):
        registry.get("csv")
