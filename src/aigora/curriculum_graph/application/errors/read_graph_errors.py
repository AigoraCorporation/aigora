"""Errors raised by read-only graph access (ADR-007).

Each error maps one-to-one to a canonical API error code. `graph_version` is
set only when the failure happened against a known, active graph version.
"""
from __future__ import annotations


class ReadGraphError(Exception):
    """Base class for read-only graph access errors."""

    code: str = "CG_INTERNAL"

    def __init__(self, message: str, *, graph_version: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.graph_version = graph_version


class GraphNodeNotFoundError(ReadGraphError):
    """A requested node id does not exist in the active graph version."""

    code = "CG_NODE_NOT_FOUND"


class GraphProfileNotFoundError(ReadGraphError):
    """A requested curriculum profile id does not exist in the active graph version."""

    code = "CG_PROFILE_NOT_FOUND"


class GraphVersionMismatchError(ReadGraphError):
    """The caller expected a graph version that is not the active one."""

    code = "CG_INVALID_GRAPH_VERSION"


class GraphUnavailableError(ReadGraphError):
    """No published graph can be served (not loaded, store unreachable or incomplete)."""

    code = "CG_GRAPH_UNAVAILABLE"


class InvalidReadRequestError(ReadGraphError):
    """Input validation failed (missing ids, invalid bounds, malformed tokens)."""

    code = "CG_INVALID_REQUEST"
