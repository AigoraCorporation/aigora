from __future__ import annotations

import re
from dataclasses import dataclass, field

from changelog_generator.task_collector import ReleaseTask


@dataclass
class ChangelogReleaseDraft:
    added: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    fixed: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)


class ChangelogDraftParseError(Exception):
    pass


class ChangelogConsolidator:
    """Parses '## Changelog Entry Draft' sections from release tasks
    and consolidates them into a single ChangelogReleaseDraft.

    Expected task body structure:

        ## Changelog Entry Draft

        ### Added
        - ...

        ### Changed
        - ...

        ### Fixed
        - ...

        ### Removed
        - ...
    """

    _DRAFT_SECTION = re.compile(
        r"##\s+Changelog Entry Draft\b(.+?)(?=\n##\s|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    _CATEGORY = {
        "added": re.compile(r"###\s+Added\b(.+?)(?=###|\Z)", re.IGNORECASE | re.DOTALL),
        "changed": re.compile(r"###\s+Changed\b(.+?)(?=###|\Z)", re.IGNORECASE | re.DOTALL),
        "fixed": re.compile(r"###\s+Fixed\b(.+?)(?=###|\Z)", re.IGNORECASE | re.DOTALL),
        "removed": re.compile(r"###\s+Removed\b(.+?)(?=###|\Z)", re.IGNORECASE | re.DOTALL),
    }

    def consolidate(self, tasks: list[ReleaseTask]) -> ChangelogReleaseDraft:
        draft = ChangelogReleaseDraft()
        for task in tasks:
            task_draft = self._parse_task(task)
            draft.added.extend(task_draft.added)
            draft.changed.extend(task_draft.changed)
            draft.fixed.extend(task_draft.fixed)
            draft.removed.extend(task_draft.removed)
        return draft

    def _parse_task(self, task: ReleaseTask) -> ChangelogReleaseDraft:
        section_match = self._DRAFT_SECTION.search(task.body)
        if not section_match:
            raise ChangelogDraftParseError(
                f"Task #{task.number} ({task.title!r}) does not contain "
                "a '## Changelog Entry Draft' section."
            )
        section = section_match.group(1)
        return ChangelogReleaseDraft(
            added=self._extract_items(self._CATEGORY["added"], section),
            changed=self._extract_items(self._CATEGORY["changed"], section),
            fixed=self._extract_items(self._CATEGORY["fixed"], section),
            removed=self._extract_items(self._CATEGORY["removed"], section),
        )

    def _extract_items(self, pattern: re.Pattern, section: str) -> list[str]:
        m = pattern.search(section)
        if not m:
            return []
        return [
            line.lstrip("-* ").strip()
            for line in m.group(1).splitlines()
            if line.strip().startswith(("-", "*"))
        ]
