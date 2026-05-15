from __future__ import annotations

from dataclasses import dataclass

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph


@dataclass(frozen=True)
class LoadGraphResult:
    """Output model returned by LoadGraphUseCase."""

    graph: CurriculumGraph
    nodes_loaded: int
    edges_loaded: int
    profiles_loaded: int
    version: str
