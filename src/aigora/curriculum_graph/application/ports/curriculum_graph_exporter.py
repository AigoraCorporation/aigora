from __future__ import annotations

from pathlib import Path
from typing import Protocol

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph


class CurriculumGraphExporter(Protocol):
    """Port for exporting a CurriculumGraph to an external representation."""

    def export(self, graph: CurriculumGraph, output_dir: str | Path) -> dict[str, Path]:
        ...
