from __future__ import annotations

from aigora.curriculum_graph.application.ports.curriculum_graph_exporter import CurriculumGraphExporter
from aigora.curriculum_graph.application.errors.export_graph_errors import (
    UnsupportedCurriculumGraphExportFormatError,
)
from aigora.curriculum_graph.application.use_cases.export_graph.curriculum_graph_export_format import (
    CurriculumGraphExportFormat,
)


class CurriculumGraphExporterRegistry:
    """Strategy registry/factory for graph exporters."""

    def __init__(self, exporters: dict[CurriculumGraphExportFormat | str, CurriculumGraphExporter]) -> None:
        self._exporters = {
            CurriculumGraphExportFormat.from_value(key): value for key, value in exporters.items()
        }

    def get(self, output_format: CurriculumGraphExportFormat | str) -> CurriculumGraphExporter:
        try:
            normalized_format = CurriculumGraphExportFormat.from_value(output_format)
        except ValueError as exc:
            supported = self._supported_formats()
            raise UnsupportedCurriculumGraphExportFormatError(
                f"Unsupported graph export format: {output_format!r}. "
                f"Supported formats: {supported}."
            ) from exc

        try:
            return self._exporters[normalized_format]
        except KeyError as exc:
            supported = self._supported_formats()
            raise UnsupportedCurriculumGraphExportFormatError(
                f"Unsupported graph export format: {normalized_format.value!r}. "
                f"Supported formats: {supported}."
            ) from exc

    def _supported_formats(self) -> str:
        return ", ".join(sorted(item.value for item in self._exporters)) or "none"
