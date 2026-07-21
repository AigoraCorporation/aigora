from __future__ import annotations

from pathlib import Path

from changelog_generator.changelog_consolidator import ChangelogReleaseDraft
from changelog_generator.release_detector import ReleaseMetadata

_CHANGELOG_HEADER = "# Changelog"


class ChangelogWriter:
    """Renders a ChangelogReleaseDraft into a CHANGELOG.md block
    and prepends it to an existing CHANGELOG.md file.

    Rendering rules:
    - Format: ## [version] - planned_date
    - Only non-empty categories are included
    - New entry is inserted after the file header, before the first ## [...] entry
    - Operation is idempotent: if the version already exists, the file is not modified
    """

    def render(self, release: ReleaseMetadata, draft: ChangelogReleaseDraft) -> str:
        lines: list[str] = [f"## [{release.version}] - {release.planned_date}", ""]
        for category, items in [
            ("Added", draft.added),
            ("Changed", draft.changed),
            ("Fixed", draft.fixed),
            ("Removed", draft.removed),
        ]:
            if items:
                lines.append(f"### {category}")
                lines.extend(f"- {item}" for item in items)
                lines.append("")
        return "\n".join(lines).rstrip("\n") + "\n"

    def prepend_to_changelog(
        self,
        entry: str,
        changelog_path: str | Path,
    ) -> None:
        path = Path(changelog_path)
        existing = path.read_text(encoding="utf-8") if path.exists() else ""

        version_token = self._extract_version_token(entry)
        if version_token and version_token in existing:
            return  # idempotent: entry for this version already present

        if not existing:
            header = (
                f"{_CHANGELOG_HEADER}\n\n"
                "All notable changes to this project will be documented in this file.\n\n"
            )
            path.write_text(header + entry, encoding="utf-8")
            return

        first_release_pos = existing.find("\n## [")
        if first_release_pos == -1:
            path.write_text(existing.rstrip("\n") + "\n\n" + entry, encoding="utf-8")
        else:
            before = existing[: first_release_pos + 1]
            after = existing[first_release_pos + 1 :]
            path.write_text(before + entry + "\n---\n\n" + after, encoding="utf-8")

    def _extract_version_token(self, entry: str) -> str | None:
        import re

        m = re.search(r"##\s+\[([^\]]+)\]", entry)
        return m.group(0) if m else None
