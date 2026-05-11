from __future__ import annotations

from enum import Enum


class CurriculumGraphExportFormat(str, Enum):
    """Supported file formats for CurriculumGraph export."""

    CSV = "csv"
    JSON = "json"
    YAML = "yaml"

    @classmethod
    def from_value(cls, value: CurriculumGraphExportFormat | str) -> CurriculumGraphExportFormat:
        if isinstance(value, cls):
            return value

        normalized = value.lower().strip()

        if normalized == "yml":
            normalized = cls.YAML.value

        try:
            return cls(normalized)
        except ValueError as exc:
            supported = ", ".join(item.value for item in cls)
            raise ValueError(
                f"Unsupported graph export format: {value!r}. Supported formats: {supported}."
            ) from exc
