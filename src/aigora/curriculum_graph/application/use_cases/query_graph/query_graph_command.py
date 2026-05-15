from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph


class QueryGraphOperation(str, Enum):
    GET_NODE = "get_node"
    GET_PREREQUISITES = "get_prerequisites"
    GET_DEPENDENTS = "get_dependents"
    GET_LEARNING_PATH = "get_learning_path"


@dataclass(frozen=True)
class QueryGraphCommand:
    """Input model for read-only Curriculum Graph queries."""

    graph: CurriculumGraph
    operation: QueryGraphOperation
    node_id: str | None = None
    start_node_id: str | None = None
    target_node_id: str | None = None
    include_soft: bool = True
