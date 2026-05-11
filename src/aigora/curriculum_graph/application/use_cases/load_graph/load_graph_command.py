from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LoadGraphCommand:
    """Input model for loading a Curriculum Graph from a file source."""

    file_path: str | Path
