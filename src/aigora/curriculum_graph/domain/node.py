from __future__ import annotations

from dataclasses import dataclass, field

from .mastery import MasteryScale


@dataclass(slots=True)
class Node:
    id: str
    name: str
    domain: str
    description: str
    mastery_criteria: MasteryScale
    error_taxonomy: list[str] = field(default_factory=list)
    prerequisite_ids: list[str] = field(default_factory=list)
    regression_ids: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.id.strip():
            raise ValueError("Node id must be non-empty.")
        if not self.name.strip():
            raise ValueError("Node name must be non-empty.")
        if not self.domain.strip():
            raise ValueError("Node domain must be non-empty.")
        if not self.description.strip():
            raise ValueError("Node description must be non-empty.")

        self.mastery_criteria.validate()

        if self.id in self.prerequisite_ids:
            raise ValueError("Node cannot list itself as prerequisite.")
        if self.id in self.regression_ids:
            raise ValueError("Node cannot list itself as regression target.")

        if len(set(self.prerequisite_ids)) != len(self.prerequisite_ids):
            raise ValueError("Node prerequisite_ids must not contain duplicates.")
        if len(set(self.regression_ids)) != len(self.regression_ids):
            raise ValueError("Node regression_ids must not contain duplicates.")