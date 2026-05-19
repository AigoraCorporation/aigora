from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReleaseMetadata:
    version: str
    name: str
    planned_date: str
    status: str
    details_url: str


class ReleaseDetectionError(Exception):
    pass


class ReleaseDetector:
    """Detects the current in-progress release from the README.md Release Roadmap table.

    The current release is defined as the first row in the roadmap table where:
    - Status contains 'In Progress'
    - Details contains a [Plan] link
    """

    _IN_PROGRESS = "In Progress"
    _PLAN_PATTERN = re.compile(r"\[Plan\]\(([^)]+)\)")
    _TABLE_HEADER = re.compile(
        r"\|\s*Version\s*\|\s*Name\s*\|\s*Status\s*\|\s*Planned Date\s*\|\s*Details\s*\|",
        re.IGNORECASE,
    )
    _SEPARATOR = re.compile(r"^\|[-| :]+\|$")
    _ROW_PATTERN = re.compile(
        r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|$"
    )

    def detect(self, readme_path: str | Path) -> ReleaseMetadata:
        content = self._read_file(readme_path)
        rows = self._parse_roadmap_table(content)
        return self._find_current_release(rows)

    def _read_file(self, path: str | Path) -> str:
        try:
            return Path(path).read_text(encoding="utf-8")
        except OSError as exc:
            raise ReleaseDetectionError(f"Could not read README: {path}") from exc

    def _parse_roadmap_table(self, content: str) -> list[dict[str, str]]:
        lines = content.splitlines()
        header_idx = next(
            (i for i, line in enumerate(lines) if self._TABLE_HEADER.search(line)),
            None,
        )
        if header_idx is None:
            raise ReleaseDetectionError(
                "Could not find the Release Roadmap table in README. "
                "Expected a table with columns: Version | Name | Status | Planned Date | Details."
            )

        rows: list[dict[str, str]] = []
        for line in lines[header_idx + 2 :]:
            stripped = line.strip()
            if not stripped.startswith("|"):
                break
            if self._SEPARATOR.match(stripped):
                continue
            m = self._ROW_PATTERN.match(stripped)
            if m:
                rows.append(
                    {
                        "version": m.group(1).strip(),
                        "name": m.group(2).strip(),
                        "status": m.group(3).strip(),
                        "planned_date": m.group(4).strip(),
                        "details": m.group(5).strip(),
                    }
                )
        return rows

    def _find_current_release(self, rows: list[dict[str, str]]) -> ReleaseMetadata:
        candidates = [
            row
            for row in rows
            if self._IN_PROGRESS in row["status"]
            and self._PLAN_PATTERN.search(row["details"])
        ]
        if not candidates:
            raise ReleaseDetectionError(
                "No current release found in README Release Roadmap. "
                "Expected a row with '🚧 In Progress' status and a [Plan] link in Details."
            )
        if len(candidates) > 1:
            versions = ", ".join(row["version"] for row in candidates)
            raise ReleaseDetectionError(
                f"Multiple releases marked as 'In Progress' in README Release Roadmap: {versions}. "
                "Only one release should be 'In Progress' at a time."
            )

        row = candidates[0]
        details_match = self._PLAN_PATTERN.search(row["details"])
        return ReleaseMetadata(
            version=row["version"],
            name=row["name"],
            planned_date=row["planned_date"],
            status=row["status"],
            details_url=details_match.group(1) if details_match else "",
        )
