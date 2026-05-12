from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.entities.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.entities.edge import Edge
from aigora.curriculum_graph.domain.entities.node import Node


@dataclass
class GraphLoadingContext:
    """Mutable context shared by graph loading pipeline steps."""

    file_path: Path
    payload: dict[str, Any] | None = None
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    profiles: list[CurriculumProfile] = field(default_factory=list)
    version: str | None = None
    graph: CurriculumGraph | None = None
