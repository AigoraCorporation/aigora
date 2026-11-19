"""Commands accepted by ReadGraphUseCase (ADR-004).

`expected_version` is the caller's optional graph version selector; `None` or
an empty string means "the active version".
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GetGraphMetadataCommand:
    expected_version: str | None = None


@dataclass(frozen=True)
class GetNodeCommand:
    node_id: str
    expected_version: str | None = None


@dataclass(frozen=True)
class ListNodesCommand:
    domain: str | None = None
    profile_id: str | None = None
    offset: int = 0
    limit: int = 100
    expected_version: str | None = None


@dataclass(frozen=True)
class GetPrerequisitesCommand:
    node_id: str
    include_soft: bool = True
    expected_version: str | None = None


@dataclass(frozen=True)
class GetRegressionTargetsCommand:
    node_id: str
    expected_version: str | None = None


@dataclass(frozen=True)
class GetLearningPathCommand:
    start_node_id: str
    target_node_id: str
    include_soft: bool = True
    expected_version: str | None = None


ReadGraphCommand = (
    GetGraphMetadataCommand
    | GetNodeCommand
    | ListNodesCommand
    | GetPrerequisitesCommand
    | GetRegressionTargetsCommand
    | GetLearningPathCommand
)
