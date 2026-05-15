from __future__ import annotations


class GraphVersion(str):
    """Strongly typed version for a Curriculum Graph snapshot."""

    def __new__(cls, value: str) -> GraphVersion:
        normalized = str(value)
        return str.__new__(cls, normalized)
