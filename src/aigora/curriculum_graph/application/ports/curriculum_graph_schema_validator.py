from __future__ import annotations

from typing import Any, Protocol


class CurriculumGraphSchemaValidatorPort(Protocol):
    """Port for validating a raw graph payload before mapping."""

    def validate(self, payload: dict[str, Any]) -> None:
        ...
