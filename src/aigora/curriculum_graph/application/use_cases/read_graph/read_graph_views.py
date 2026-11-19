"""Application read models returned by ReadGraphUseCase.

Delivery adapters (gRPC) depend on these views instead of domain entities, so
the presentation layer never imports the domain (import-linter contract).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PrerequisiteKind(str, Enum):
    HARD = "hard"
    SOFT = "soft"


@dataclass(frozen=True, slots=True)
class MasteryCriterionView:
    level: int
    level_name: str
    description: str


@dataclass(frozen=True, slots=True)
class NodeView:
    id: str
    name: str
    domain: str
    description: str
    mastery_criteria: tuple[MasteryCriterionView, ...]
    error_taxonomy: tuple[str, ...]
    prerequisite_ids: tuple[str, ...]
    regression_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PrerequisiteView:
    node: NodeView
    kind: PrerequisiteKind


@dataclass(frozen=True, slots=True)
class GraphMetadataView:
    node_count: int
    edge_count: int
    profile_count: int
    profile_ids: tuple[str, ...]
    domains: tuple[str, ...]
