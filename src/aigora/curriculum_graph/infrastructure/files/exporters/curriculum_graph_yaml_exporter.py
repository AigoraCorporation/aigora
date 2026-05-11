from __future__ import annotations

from pathlib import Path

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.infrastructure.files.errors import (
    CurriculumGraphYamlExporterError,
)
from aigora.curriculum_graph.infrastructure.files.serialization.curriculum_graph_serializer import (
    CurriculumGraphSerializer,
)


class CurriculumGraphYamlExporter:
    """Exports an already loaded CurriculumGraph as a YAML document."""

    FILE_NAME = "graph.yaml"

    def __init__(self, serializer: CurriculumGraphSerializer | None = None) -> None:
        self._serializer = serializer or CurriculumGraphSerializer()

    def export(self, graph: CurriculumGraph, output_dir: str | Path) -> dict[str, Path]:
        output_path = Path(output_dir)

        try:
            self._ensure_output_directory(output_path)
            destination = output_path / self.FILE_NAME
            destination.write_text(
                self._serializer.serialize(graph, "yaml"),
                encoding="utf-8",
            )
            return {self.FILE_NAME: destination}
        except Exception as exc:
            raise CurriculumGraphYamlExporterError(
                f"Failed to export CurriculumGraph YAML file to: {output_path}"
            ) from exc

    def _ensure_output_directory(self, output_path: Path) -> None:
        if output_path.exists() and not output_path.is_dir():
            raise NotADirectoryError(f"Output path is not a directory: {output_path}")

        output_path.mkdir(parents=True, exist_ok=True)
