from enum import Enum, IntEnum


class MasteryLevel(IntEnum):
    """
    Mastery scale used across the entire system for all canonical nodes.

    Level 0 (UNEXPOSED) is the initial state — the student has not yet
    encountered this concept. It is not a valid curriculum target.
    Targets must be in the range [1, 5].
    """

    UNEXPOSED = 0
    RECOGNISES = 1
    GUIDED = 2
    INDEPENDENT = 3
    EFFICIENT = 4
    TRANSFERABLE = 5


class EdgeType(str, Enum):
    """Type of prerequisite relationship between two canonical nodes."""

    HARD = "hard"
    # Orchestrator must enforce: the dependent node cannot be meaningfully
    # attempted without sufficient mastery of the prerequisite.

    SOFT = "soft"
    # Advisory: the dependent node is significantly easier with the prerequisite,
    # but not impossible without it. The orchestrator recommends but does not enforce.


class NodeStatus(str, Enum):
    """Lifecycle status of a canonical node."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"


class ProfileStatus(str, Enum):
    """Lifecycle status of a curriculum profile."""

    ACTIVE = "active"
    RETIRED = "retired"
