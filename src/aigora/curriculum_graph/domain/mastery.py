from __future__ import annotations

from dataclasses import dataclass, field

from .enums import MasteryLevel


@dataclass(frozen=True, slots=True)
class MasteryCriterion:
    level: MasteryLevel
    description: str


@dataclass(frozen=True, slots=True)
class MasteryScale:
    criteria_by_level: dict[MasteryLevel, MasteryCriterion] = field(default_factory=dict)

    def get(self, level: MasteryLevel) -> MasteryCriterion:
        try:
            return self.criteria_by_level[level]
        except KeyError as exc:
            raise KeyError(f"Mastery level not defined: {level}") from exc

    def has_level(self, level: MasteryLevel) -> bool:
        return level in self.criteria_by_level

    def validate(self) -> None:
        if not self.criteria_by_level:
            raise ValueError("Mastery scale must define at least one mastery criterion.")

        for level, criterion in self.criteria_by_level.items():
            if criterion.level != level:
                raise ValueError(
                    "Mastery scale is inconsistent: dictionary key must match criterion.level."
                )
            if not criterion.description.strip():
                raise ValueError(
                    f"Mastery criterion for level {level} must have a non-empty description."
                )