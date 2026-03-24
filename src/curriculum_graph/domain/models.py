from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .enums import EdgeType, NodeStatus, ProfileStatus


@dataclass(frozen=True)
class PrerequisiteEdge:
    """A directed prerequisite relationship pointing to a canonical node."""

    node_id: str
    edge_type: EdgeType


@dataclass(frozen=True)
class MasteryCriteria:
    """
    Describes what demonstrating mastery looks like at each level for a node.

    Level 0 (Unexposed) has no criteria — the student has not encountered the
    concept yet. Levels 1–5 must describe a genuine and distinguishable
    progression of competence specific to this concept.
    """

    level_1: str
    level_2: str
    level_3: str
    level_4: str
    level_5: str

    def for_level(self, level: int) -> str:
        """Return the criteria description for the given mastery level (1–5)."""
        mapping = {
            1: self.level_1,
            2: self.level_2,
            3: self.level_3,
            4: self.level_4,
            5: self.level_5,
        }
        if level not in mapping:
            raise ValueError(f"Mastery level must be between 1 and 5, got {level}")
        return mapping[level]

    def as_dict(self) -> dict[int, str]:
        return {
            1: self.level_1,
            2: self.level_2,
            3: self.level_3,
            4: self.level_4,
            5: self.level_5,
        }


@dataclass(frozen=True)
class ErrorTaxonomyEntry:
    """A named misconception or error pattern specific to a canonical node."""

    name: str
    description: str


@dataclass(frozen=True)
class CanonicalNode:
    """
    A single, well-scoped mathematical concept in the canonical graph.

    Nodes are mathematical primitives. They carry no exam information.
    Node IDs are permanent — they never change after a node is published.
    Once published, renaming a concept does not change its id.
    """

    id: str
    name: str
    domain: str
    description: str
    mastery_criteria: MasteryCriteria
    error_taxonomy: tuple[ErrorTaxonomyEntry, ...]
    prerequisite_ids: tuple[PrerequisiteEdge, ...]
    regression_ids: tuple[str, ...]
    status: NodeStatus = NodeStatus.ACTIVE
    deprecated_since: Optional[str] = None
    replaced_by: Optional[str] = None


@dataclass(frozen=True)
class ProfileNode:
    """
    A canonical node as it appears within a curriculum profile,
    carrying the exam-specific mastery target and relative weight.
    """

    node_id: str
    mastery_target: int  # 1–5; 0 (Unexposed) is invalid as a curriculum target
    weight: float  # strictly positive


@dataclass(frozen=True)
class ExamSkillOverlayEntry:
    """
    A non-mathematical exam competency layered over canonical content mastery.

    Examples: time pressure handling, strategic skipping, multi-step problem parsing.
    Mathematical concepts must never appear here — they belong in a canonical node.
    """

    name: str
    description: str


@dataclass(frozen=True)
class CurriculumProfile:
    """
    An exam-specific lens applied over the canonical graph.

    A profile selects, weights, and sequences canonical nodes for a specific
    exam or educational context. It does not define new mathematical content.
    Profile IDs are permanent. A new exam edition results in a new profile,
    not a mutation of an existing one.
    """

    id: str
    name: str
    version: str
    requires_graph_version: str
    required_nodes: tuple[ProfileNode, ...]
    progression_path: tuple[str, ...]  # ordered canonical node ids
    exam_skill_overlay: tuple[ExamSkillOverlayEntry, ...]
    status: ProfileStatus = ProfileStatus.ACTIVE
    retired_at: Optional[str] = None

    def required_node_ids(self) -> frozenset[str]:
        return frozenset(pn.node_id for pn in self.required_nodes)

    def mastery_target_for(self, node_id: str) -> Optional[int]:
        for pn in self.required_nodes:
            if pn.node_id == node_id:
                return pn.mastery_target
        return None

    def weight_for(self, node_id: str) -> Optional[float]:
        for pn in self.required_nodes:
            if pn.node_id == node_id:
                return pn.weight
        return None


@dataclass
class CanonicalGraph:
    """
    The in-memory representation of the full canonical graph and all registered
    profiles. Loaded and validated before any queries are executed.

    The canonical graph is the single source of truth for mathematical concept
    structure. Profiles are lenses over it. Student mastery is stored externally
    in the Student Model, not here.
    """

    version: str
    published_at: str
    nodes: dict[str, CanonicalNode]  # node_id → CanonicalNode
    profiles: dict[str, CurriculumProfile]  # profile_id → CurriculumProfile
    description: str = ""
