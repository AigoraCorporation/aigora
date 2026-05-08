from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PublishGraphCommand:
    """Input model for publishing a Curriculum Graph.

    This object carries the request data required by the application use case.
    It does not execute business logic or access infrastructure.
    """

    file_path: str | Path
    export_csv: bool = False
    csv_output_dir: str | Path | None = None
