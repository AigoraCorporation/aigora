from __future__ import annotations

from dataclasses import dataclass

from .enums import EdgeType


@dataclass(frozen=True, slots=True)
class Edge:
    type: EdgeType
    source: str
    target: str

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ValueError("Edge source must be non-empty.")
        if not self.target.strip():
            raise ValueError("Edge target must be non-empty.")
        if self.source == self.target:
            raise ValueError("Edge source and target must be different.")