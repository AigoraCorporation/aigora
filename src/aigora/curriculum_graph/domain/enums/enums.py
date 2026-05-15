from __future__ import annotations

from enum import Enum


class EdgeType(str, Enum):
    HARD_PREREQUISITE = "hard_prerequisite"
    SOFT_PREREQUISITE = "soft_prerequisite"
    REGRESSION_TARGET = "regression_target"


class MasteryLevel(int, Enum):
    UNEXPOSED = 0
    RECOGNISES = 1
    GUIDED = 2
    INDEPENDENT = 3
    EFFICIENT = 4
    TRANSFERABLE = 5