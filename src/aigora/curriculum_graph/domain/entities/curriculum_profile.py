from __future__ import annotations

from dataclasses import dataclass, field

from aigora.curriculum_graph.domain.enums.enums import MasteryLevel
from aigora.curriculum_graph.domain.value_objects.node_id import NodeId
from aigora.curriculum_graph.domain.value_objects.profile_id import ProfileId


@dataclass(slots=True)
class CurriculumProfile:
    id: ProfileId | str
    name: str
    required_nodes: set[NodeId | str] = field(default_factory=set)
    mastery_targets: dict[NodeId | str, MasteryLevel] = field(default_factory=dict)
    node_weights: dict[NodeId | str, float] = field(default_factory=dict)
    progression_path: list[NodeId | str] = field(default_factory=list)
    exam_skill_overlay: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_self()
        self.id = ProfileId(self.id)
        self.required_nodes = {NodeId(node_id) for node_id in self.required_nodes}
        self.mastery_targets = {NodeId(node_id): level for node_id, level in self.mastery_targets.items()}
        self.node_weights = {NodeId(node_id): weight for node_id, weight in self.node_weights.items()}
        self.progression_path = [NodeId(node_id) for node_id in self.progression_path]

    def _validate_self(self) -> None:
        if not self.id.strip():
            raise ValueError("CurriculumProfile id must be non-empty.")
        if not self.name.strip():
            raise ValueError("CurriculumProfile name must be non-empty.")

        for node_id, weight in self.node_weights.items():
            if not node_id.strip():
                raise ValueError("CurriculumProfile node_weights cannot contain empty node ids.")
            if weight < 0:
                raise ValueError(f"Node weight must be non-negative. node_id={node_id}")

        for node_id in self.mastery_targets:
            if not node_id.strip():
                raise ValueError("CurriculumProfile mastery_targets cannot contain empty node ids.")

        for node_id in self.progression_path:
            if not node_id.strip():
                raise ValueError("CurriculumProfile progression_path cannot contain empty node ids.")

    def referenced_node_ids(self) -> set[str]:
        return (
            set(self.required_nodes)
            | set(self.mastery_targets.keys())
            | set(self.node_weights.keys())
            | set(self.progression_path)
        )