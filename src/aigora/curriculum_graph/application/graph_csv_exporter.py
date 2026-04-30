from __future__ import annotations

import csv
import shutil
import tempfile
from pathlib import Path
from typing import Any

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph


class GraphCsvExporterError(Exception):
    """Raised when CurriculumGraph CSV export fails."""


class GraphCsvExporter:
    """Exports an already loaded CurriculumGraph into canonical CSV files."""

    REQUIRED_FILES = (
        "nodes.csv",
        "edges.csv",
        "profiles.csv",
        "profile_mastery_targets.csv",
        "profile_node_weights.csv",
        "profile_progression_paths.csv",
    )

    def export(self, graph: CurriculumGraph, output_dir: str | Path) -> dict[str, Path]:
        output_path = Path(output_dir)

        try:
            self._ensure_output_directory(output_path)

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                self._write_nodes(graph, temp_path / "nodes.csv")
                self._write_edges(graph, temp_path / "edges.csv")
                self._write_profiles(graph, temp_path / "profiles.csv")
                self._write_profile_mastery_targets(
                    graph,
                    temp_path / "profile_mastery_targets.csv",
                )
                self._write_profile_node_weights(
                    graph,
                    temp_path / "profile_node_weights.csv",
                )
                self._write_profile_progression_paths(
                    graph,
                    temp_path / "profile_progression_paths.csv",
                )

                exported_paths: dict[str, Path] = {}

                for file_name in self.REQUIRED_FILES:
                    destination = output_path / file_name
                    shutil.copyfile(temp_path / file_name, destination)
                    exported_paths[file_name] = destination

                return exported_paths

        except Exception as exc:
            raise GraphCsvExporterError(
                f"Failed to export CurriculumGraph CSV files to: {output_path}"
            ) from exc

    def _ensure_output_directory(self, output_path: Path) -> None:
        if output_path.exists() and not output_path.is_dir():
            raise NotADirectoryError(f"Output path is not a directory: {output_path}")

        output_path.mkdir(parents=True, exist_ok=True)

    def _write_nodes(self, graph: CurriculumGraph, file_path: Path) -> None:
        rows = [
            {
                "id": node.id,
                "name": node.name,
                "domain": node.domain,
                "description": node.description,
            }
            for node in sorted(graph.nodes.values(), key=lambda item: item.id)
        ]

        self._write_csv(
            file_path,
            fieldnames=["id", "name", "domain", "description"],
            rows=rows,
        )

    def _write_edges(self, graph: CurriculumGraph, file_path: Path) -> None:
        rows = [
            {
                "type": self._enum_value(edge.type),
                "source": edge.source,
                "target": edge.target,
            }
            for edge in sorted(
                graph.edges,
                key=lambda item: (
                    self._enum_value(item.type),
                    item.source,
                    item.target,
                ),
            )
        ]

        self._write_csv(
            file_path,
            fieldnames=["type", "source", "target"],
            rows=rows,
        )

    def _write_profiles(self, graph: CurriculumGraph, file_path: Path) -> None:
        rows = [
            {
                "id": profile.id,
                "name": profile.name,
            }
            for profile in sorted(graph.profiles.values(), key=lambda item: item.id)
        ]

        self._write_csv(
            file_path,
            fieldnames=["id", "name"],
            rows=rows,
        )

    def _write_profile_mastery_targets(
        self,
        graph: CurriculumGraph,
        file_path: Path,
    ) -> None:
        rows: list[dict[str, Any]] = []

        for profile in sorted(graph.profiles.values(), key=lambda item: item.id):
            for node_id in sorted(profile.mastery_targets.keys()):
                rows.append(
                    {
                        "profile_id": profile.id,
                        "node_id": node_id,
                        "mastery_level": self._enum_value(
                            profile.mastery_targets[node_id]
                        ),
                    }
                )

        self._write_csv(
            file_path,
            fieldnames=["profile_id", "node_id", "mastery_level"],
            rows=rows,
        )

    def _write_profile_node_weights(
        self,
        graph: CurriculumGraph,
        file_path: Path,
    ) -> None:
        rows: list[dict[str, Any]] = []

        for profile in sorted(graph.profiles.values(), key=lambda item: item.id):
            for node_id in sorted(profile.node_weights.keys()):
                rows.append(
                    {
                        "profile_id": profile.id,
                        "node_id": node_id,
                        "weight": profile.node_weights[node_id],
                    }
                )

        self._write_csv(
            file_path,
            fieldnames=["profile_id", "node_id", "weight"],
            rows=rows,
        )

    def _write_profile_progression_paths(
        self,
        graph: CurriculumGraph,
        file_path: Path,
    ) -> None:
        rows: list[dict[str, Any]] = []

        for profile in sorted(graph.profiles.values(), key=lambda item: item.id):
            for position, node_id in enumerate(profile.progression_path):
                rows.append(
                    {
                        "profile_id": profile.id,
                        "position": position,
                        "node_id": node_id,
                    }
                )

        self._write_csv(
            file_path,
            fieldnames=["profile_id", "position", "node_id"],
            rows=rows,
        )

    def _write_csv(
        self,
        file_path: Path,
        fieldnames: list[str],
        rows: list[dict[str, Any]],
    ) -> None:
        with file_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _enum_value(self, value: Any) -> Any:
        return getattr(value, "value", value)