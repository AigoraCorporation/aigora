from __future__ import annotations

from typing import Protocol

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph


class CurriculumGraphReader(Protocol):
    """Port returning the currently published CurriculumGraph snapshot (ADR-007).

    Implementations live in the infrastructure layer and must:

    - return the complete graph of the active published version, with
      `graph.version` set;
    - raise `GraphUnavailableError` when no published graph exists, the store
      is unreachable, or the stored data cannot be rebuilt into a valid graph.
    """

    def load_published(self) -> CurriculumGraph:
        ...
