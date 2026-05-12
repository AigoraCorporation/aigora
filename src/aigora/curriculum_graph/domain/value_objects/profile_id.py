from __future__ import annotations


class ProfileId(str):
    """Strongly typed identifier for a Curriculum Profile."""

    def __new__(cls, value: str) -> ProfileId:
        normalized = str(value)
        if not normalized.strip():
            raise ValueError("CurriculumProfile id must be non-empty.")
        return str.__new__(cls, normalized)
