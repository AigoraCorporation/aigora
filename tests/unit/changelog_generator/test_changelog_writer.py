from __future__ import annotations

import pytest

from changelog_generator.changelog_consolidator import ChangelogReleaseDraft
from changelog_generator.changelog_writer import ChangelogWriter
from changelog_generator.release_detector import ReleaseMetadata

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXISTING_CHANGELOG = """\
# Changelog

All notable changes to this project will be documented in this file.

## [v0.2.1] - 2026-05-15

### Added

- Existing feature
"""


def make_release(version: str = "v0.2.2", date: str = "2026-06-15") -> ReleaseMetadata:
    return ReleaseMetadata(
        version=version,
        name="Curriculum Graph API Foundation",
        planned_date=date,
        status="🚧 In Progress",
        details_url="https://example.com/186",
    )


def make_draft(
    added: list[str] | None = None,
    changed: list[str] | None = None,
    fixed: list[str] | None = None,
    removed: list[str] | None = None,
) -> ChangelogReleaseDraft:
    return ChangelogReleaseDraft(
        added=added or [],
        changed=changed or [],
        fixed=fixed or [],
        removed=removed or [],
    )


# ---------------------------------------------------------------------------
# render() tests
# ---------------------------------------------------------------------------


def test_render_produces_version_and_date_heading():
    entry = ChangelogWriter().render(make_release(), make_draft(added=["Feature A"]))

    assert entry.startswith("## [v0.2.2] - 2026-06-15")


def test_render_includes_non_empty_categories():
    draft = make_draft(added=["Feature A"], fixed=["Bug B"])
    entry = ChangelogWriter().render(make_release(), draft)

    assert "### Added" in entry
    assert "- Feature A" in entry
    assert "### Fixed" in entry
    assert "- Bug B" in entry


def test_render_excludes_empty_categories():
    draft = make_draft(added=["Feature A"])
    entry = ChangelogWriter().render(make_release(), draft)

    assert "### Changed" not in entry
    assert "### Fixed" not in entry
    assert "### Removed" not in entry


def test_render_preserves_category_order():
    draft = make_draft(
        added=["A"],
        changed=["C"],
        fixed=["F"],
        removed=["R"],
    )
    entry = ChangelogWriter().render(make_release(), draft)

    added_pos = entry.index("### Added")
    changed_pos = entry.index("### Changed")
    fixed_pos = entry.index("### Fixed")
    removed_pos = entry.index("### Removed")

    assert added_pos < changed_pos < fixed_pos < removed_pos


# ---------------------------------------------------------------------------
# prepend_to_changelog() tests
# ---------------------------------------------------------------------------


def test_prepends_entry_before_existing_releases(tmp_path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(EXISTING_CHANGELOG, encoding="utf-8")

    draft = make_draft(added=["New feature"])
    entry = ChangelogWriter().render(make_release(), draft)
    ChangelogWriter().prepend_to_changelog(entry, changelog)

    content = changelog.read_text(encoding="utf-8")
    new_pos = content.index("## [v0.2.2]")
    old_pos = content.index("## [v0.2.1]")
    assert new_pos < old_pos


def test_creates_changelog_with_header_when_file_does_not_exist(tmp_path):
    changelog = tmp_path / "CHANGELOG.md"

    draft = make_draft(added=["First feature"])
    entry = ChangelogWriter().render(make_release(), draft)
    ChangelogWriter().prepend_to_changelog(entry, changelog)

    content = changelog.read_text(encoding="utf-8")
    assert "# Changelog" in content
    assert "## [v0.2.2]" in content


def test_is_idempotent_when_version_already_present(tmp_path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(EXISTING_CHANGELOG, encoding="utf-8")

    # Write entry for a version already in the file
    old_release = make_release(version="v0.2.1", date="2026-05-15")
    draft = make_draft(added=["Duplicate"])
    entry = ChangelogWriter().render(old_release, draft)

    ChangelogWriter().prepend_to_changelog(entry, changelog)

    content = changelog.read_text(encoding="utf-8")
    assert content.count("## [v0.2.1]") == 1


def test_prepend_preserves_existing_content(tmp_path):
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(EXISTING_CHANGELOG, encoding="utf-8")

    draft = make_draft(added=["Feature"])
    entry = ChangelogWriter().render(make_release(), draft)
    ChangelogWriter().prepend_to_changelog(entry, changelog)

    content = changelog.read_text(encoding="utf-8")
    assert "Existing feature" in content
