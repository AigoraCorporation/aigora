from __future__ import annotations

from dataclasses import dataclass

from aigora.curriculum_graph.domain.enums.enums import EdgeType
from aigora.curriculum_graph.domain.value_objects.node_id import NodeId


@dataclass(frozen=True, slots=True)
class Edge:
    type: EdgeType
    source: NodeId | str
    target: NodeId | str

    def __post_init__(self) -> None:
        if not str(self.source).strip():
            raise ValueError("Edge source must be non-empty.")
        if not str(self.target).strip():
            raise ValueError("Edge target must be non-empty.")

        object.__setattr__(self, "source", NodeId(self.source))
        object.__setattr__(self, "target", NodeId(self.target))

        if self.source == self.target:
            raise ValueError("Edge source and target must be different.")
