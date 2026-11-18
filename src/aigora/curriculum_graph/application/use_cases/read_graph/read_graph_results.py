"""Results returned by ReadGraphUseCase. Every result carries `graph_version` (ADR-007)."""
from __future__ import annotations

from dataclasses import dataclass

from .read_graph_views import GraphMetadataView, NodeView, PrerequisiteView


@dataclass(frozen=True)
class GetGraphMetadataResult:
    graph_version: str
    metadata: GraphMetadataView


@dataclass(frozen=True)
class GetNodeResult:
    graph_version: str
    node: NodeView


@dataclass(frozen=True)
class ListNodesResult:
    graph_version: str
    nodes: tuple[NodeView, ...]
    total_size: int
    next_offset: int | None


@dataclass(frozen=True)
class GetPrerequisitesResult:
    graph_version: str
    prerequisites: tuple[PrerequisiteView, ...]


@dataclass(frozen=True)
class GetRegressionTargetsResult:
    graph_version: str
    targets: tuple[NodeView, ...]


@dataclass(frozen=True)
class GetLearningPathResult:
    graph_version: str
    path_found: bool
    path: tuple[NodeView, ...]
