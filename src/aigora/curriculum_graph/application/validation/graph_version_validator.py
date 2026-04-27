from __future__ import annotations

import re

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.application.validation.versioning_errors import InvalidVersionFormatError, MissingVersionError

_SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


class GraphVersionValidator:
    """Validates version metadata on a CurriculumGraph.

    This validator enforces that version information is present and conforms
    to the semantic versioning format (MAJOR.MINOR.PATCH).
    """

    def validate(self, graph: CurriculumGraph) -> None:
        if graph.version is None:
            raise MissingVersionError(
                "CurriculumGraph is missing required version metadata."
            )
        self._validate_format(graph.version)

    def _validate_format(self, version: str) -> None:
        if not _SEMVER_PATTERN.fullmatch(version):
            raise InvalidVersionFormatError(
                f"Version {version!r} does not conform to the expected format 'MAJOR.MINOR.PATCH' "
                f"(e.g. '1.0.0')."
            )
