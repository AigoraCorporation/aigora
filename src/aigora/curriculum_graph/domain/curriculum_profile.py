from __future__ import annotations

from dataclasses import dataclass, field

from .enums import MasteryLevel


@dataclass(slots=True)
class CurriculumProfile:
    id: str
    name: str
    required_nodes: set[str] = field(default_factory=set)
    mastery_targets: dict[str, MasteryLevel] = field(default_factory=dict)
    node_weights: dict[str, float] = field(default_factory=dict)
    progression_path: list[str] = field(default_factory=list)
    exam_skill_overlay: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate_self()

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