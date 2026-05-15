from __future__ import annotations


class NodeId(str):
    """Strongly typed identifier for a Curriculum Graph node."""

    def __new__(cls, value: str) -> NodeId:
        normalized = str(value)
        if not normalized.strip():
            raise ValueError("Node id must be non-empty.")
        return str.__new__(cls, normalized)
