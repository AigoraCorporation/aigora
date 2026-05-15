from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol


class CurriculumGraphFileParserPort(Protocol):
    """Port for parsing a graph file into a raw payload."""

    def parse_file(self, file_path: str | Path) -> dict[str, Any]:
        ...
