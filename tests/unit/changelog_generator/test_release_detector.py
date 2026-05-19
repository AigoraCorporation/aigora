from __future__ import annotations

import pytest

from changelog_generator.release_detector import (
    ReleaseDetectionError,
    ReleaseDetector,
    ReleaseMetadata,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

README_HAPPY_PATH = """\
# Project

## Releases & Roadmap

Release Roadmap:

| Version | Name | Status | Planned Date | Details |
|--------|------|--------|---------|---------|
| v0.2.1 | Old Release | ✅ Released | 2026-03-01 | [Notes](https://example.com/notes) |
| v0.2.2 | Curriculum Graph API Foundation | 🚧 In Progress | 2026-06-15 | [Plan](https://example.com/186) |
| v0.3.0 | Orchestrator Core | 🔜 Planned | 2026-09-01 | [Plan](https://example.com/185) |
"""

README_MULTIPLE_IN_PROGRESS = """\
# Project

Release Roadmap:

| Version | Name | Status | Planned Date | Details |
|--------|------|--------|---------|---------|
| v0.2.2 | First Release | 🚧 In Progress | 2026-06-15 | [Plan](https://example.com/186) |
| v0.3.0 | Second Release | 🚧 In Progress | 2026-09-01 | [Plan](https://example.com/185) |
"""

README_MULTIPLE_IN_PROGRESS_REVERSE = """\
# Project

Release Roadmap:

| Version | Name | Status | Planned Date | Details |
|--------|------|--------|---------|---------|
| v0.3.0 | Second Release | 🚧 In Progress | 2026-09-01 | [Plan](https://example.com/185) |
| v0.2.2 | First Release | 🚧 In Progress | 2026-06-15 | [Plan](https://example.com/186) |
"""

README_NO_IN_PROGRESS = """\
# Project

Release Roadmap:

| Version | Name | Status | Planned Date | Details |
|--------|------|--------|---------|---------|
| v0.2.1 | Old Release | ✅ Released | 2026-03-01 | [Notes](https://example.com/notes) |
"""

README_NO_TABLE = """\
# Project

Just some content, no release table here.
"""

# ---------------------------------------------------------------------------
# Scenario 1 — Happy Path
# ---------------------------------------------------------------------------


def test_detects_current_release_version_and_name(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(README_HAPPY_PATH, encoding="utf-8")

    result = ReleaseDetector().detect(readme)

    assert result.version == "v0.2.2"
    assert result.name == "Curriculum Graph API Foundation"


def test_detects_planned_date_and_details_url(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(README_HAPPY_PATH, encoding="utf-8")

    result = ReleaseDetector().detect(readme)

    assert result.planned_date == "2026-06-15"
    assert result.details_url == "https://example.com/186"


def test_returns_release_metadata_instance(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(README_HAPPY_PATH, encoding="utf-8")

    result = ReleaseDetector().detect(readme)

    assert isinstance(result, ReleaseMetadata)


# ---------------------------------------------------------------------------
# Scenario 2 — Edge Case: multiple In Progress rows
# ---------------------------------------------------------------------------


def test_ignores_released_and_planned_rows(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(README_HAPPY_PATH, encoding="utf-8")

    result = ReleaseDetector().detect(readme)

    assert result.version == "v0.2.2"
    assert "Released" not in result.status
    assert "Planned" not in result.status


def test_raises_when_multiple_in_progress_rows_exist(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(README_MULTIPLE_IN_PROGRESS, encoding="utf-8")

    with pytest.raises(ReleaseDetectionError, match="Multiple releases marked as 'In Progress'") as exc_info:
        ReleaseDetector().detect(readme)
    
    # Verify versions are listed in sorted order
    assert "v0.2.2, v0.3.0" in str(exc_info.value)


def test_error_message_sorts_versions_consistently(tmp_path):
    """Verify that multiple in-progress versions are sorted in error message."""
    readme = tmp_path / "README.md"
    readme.write_text(README_MULTIPLE_IN_PROGRESS_REVERSE, encoding="utf-8")

    with pytest.raises(ReleaseDetectionError) as exc_info:
        ReleaseDetector().detect(readme)
    
    # Even though v0.3.0 appears first in README, error should show sorted order
    assert "v0.2.2, v0.3.0" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Scenario 3 — Failure Cases
# ---------------------------------------------------------------------------


def test_raises_when_readme_has_no_roadmap_table(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(README_NO_TABLE, encoding="utf-8")

    with pytest.raises(ReleaseDetectionError, match="Could not find the Release Roadmap table"):
        ReleaseDetector().detect(readme)


def test_raises_when_no_in_progress_row_exists(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(README_NO_IN_PROGRESS, encoding="utf-8")

    with pytest.raises(ReleaseDetectionError, match="No current release found"):
        ReleaseDetector().detect(readme)


def test_raises_when_file_does_not_exist():
    with pytest.raises(ReleaseDetectionError, match="Could not read README"):
        ReleaseDetector().detect("/nonexistent/path/README.md")
