from __future__ import annotations

from dataclasses import dataclass

from aigora.curriculum_graph.domain.entities.node import Node


@dataclass(frozen=True)
class QueryGraphResult:
    """Output model returned by QueryGraphUseCase."""

    nodes: list[Node]
