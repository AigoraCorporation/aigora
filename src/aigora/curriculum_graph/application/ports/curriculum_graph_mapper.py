from __future__ import annotations

from typing import Any, Protocol

from aigora.curriculum_graph.domain.entities.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.entities.edge import Edge
from aigora.curriculum_graph.domain.entities.node import Node


class CurriculumGraphMapperPort(Protocol):
    """Port for mapping raw graph payload items into domain objects."""

    def map_node(self, payload: dict[str, Any]) -> Node:
        ...

    def map_edge(self, payload: dict[str, Any]) -> Edge:
        ...

    def map_profile(self, payload: dict[str, Any]) -> CurriculumProfile:
        ...
