from __future__ import annotations

import threading

from aigora.curriculum_graph.application.errors.read_graph_errors import (
    GraphUnavailableError,
    GraphVersionMismatchError,
    ReadGraphError,
)
from aigora.curriculum_graph.application.ports.curriculum_graph_reader import CurriculumGraphReader
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph


class PublishedGraphProvider:
    """Holds the published graph snapshot served by read-only use cases.

    The snapshot is loaded once (`load`) and served from memory. A failed load
    leaves the provider without a snapshot; requests then fail with
    `GraphUnavailableError` until a later `load` succeeds.

    Args:
        reader: Port that returns the published graph.
        required_version: Optional version the deployment must serve. When set
            and the published version differs, loading fails.
    """

    def __init__(self, reader: CurriculumGraphReader, required_version: str | None = None) -> None:
        self._reader = reader
        self._required_version = required_version or None
        self._graph: CurriculumGraph | None = None
        self._last_error: str | None = None
        self._lock = threading.Lock()

    @property
    def is_ready(self) -> bool:
        return self._graph is not None

    @property
    def graph_version(self) -> str | None:
        graph = self._graph
        return str(graph.version) if graph is not None and graph.version is not None else None

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def load(self) -> bool:
        """Load the published snapshot. Returns True when a snapshot is being served."""
        try:
            graph = self._reader.load_published()
            version = str(graph.version) if graph.version is not None else ""
            if not version:
                raise GraphUnavailableError("Published graph has no version.")
            if self._required_version is not None and version != self._required_version:
                raise GraphUnavailableError(
                    f"Published graph version {version!r} does not match the required "
                    f"version {self._required_version!r}."
                )
        except ReadGraphError as exc:
            with self._lock:
                self._graph = None
                self._last_error = exc.message
            return False
        with self._lock:
            self._graph = graph
            self._last_error = None
        return True

    def snapshot(self, expected_version: str | None = None) -> CurriculumGraph:
        """Return the served graph, checking the caller's expected version if given."""
        graph = self._graph
        if graph is None:
            raise GraphUnavailableError("No published Curriculum Graph is loaded.")
        version = str(graph.version)
        if expected_version and expected_version != version:
            raise GraphVersionMismatchError(
                f"Requested graph version {expected_version!r} is not the active version."
            )
        return graph
