from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.entities.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.entities.edge import Edge
from aigora.curriculum_graph.domain.entities.node import Node


class CurriculumGraphAssemblerPort(Protocol):
    """Port for assembling mapped domain objects into a CurriculumGraph."""

    def assemble(
        self,
        nodes: Sequence[Node],
        edges: Sequence[Edge],
        profiles: Sequence[CurriculumProfile],
        version: str | None = None,
    ) -> CurriculumGraph:
        ...
