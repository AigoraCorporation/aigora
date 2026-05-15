from __future__ import annotations

from aigora.curriculum_graph.application.use_cases.export_graph import (
    CurriculumGraphExportFormat,
    CurriculumGraphExporterRegistry,
)
from aigora.curriculum_graph.infrastructure.files.csv.curriculum_graph_csv_exporter import (
    CurriculumGraphCsvExporter,
)
from aigora.curriculum_graph.infrastructure.files.exporters.curriculum_graph_json_exporter import (
    CurriculumGraphJsonExporter,
)
from aigora.curriculum_graph.infrastructure.files.exporters.curriculum_graph_yaml_exporter import (
    CurriculumGraphYamlExporter,
)


def build_file_curriculum_graph_exporter_registry() -> CurriculumGraphExporterRegistry:
    """Compose the graph exporter strategy registry with file-based exporters."""

    return CurriculumGraphExporterRegistry(
        exporters={
            CurriculumGraphExportFormat.CSV: CurriculumGraphCsvExporter(),
            CurriculumGraphExportFormat.JSON: CurriculumGraphJsonExporter(),
            CurriculumGraphExportFormat.YAML: CurriculumGraphYamlExporter(),
        }
    )
