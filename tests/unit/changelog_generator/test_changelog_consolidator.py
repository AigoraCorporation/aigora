from __future__ import annotations

import pytest

from changelog_generator.changelog_consolidator import (
    ChangelogConsolidator,
    ChangelogDraftParseError,
    ChangelogReleaseDraft,
)
from changelog_generator.task_collector import ReleaseTask

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_task(number: int = 1, title: str = "Task", body: str = "") -> ReleaseTask:
    return ReleaseTask(
        number=number,
        title=title,
        body=body,
        state="open",
        labels=("release",),
        milestone="Curriculum Graph API Foundation",
    )


BODY_FULL = """\
## Context

Some background.

## Changelog Entry Draft

### Added
- Feature A
- Feature B

### Changed
- Updated config

### Fixed
- Fixed crash

### Removed
- Deprecated endpoint
"""

BODY_PARTIAL = """\
## Changelog Entry Draft

### Added
- Only addition
"""

BODY_CHANGED_AND_FIXED_ONLY = """\
## Changelog Entry Draft

### Changed
- Refactored pipeline

### Fixed
- Null pointer in serializer
"""

BODY_NO_DRAFT = """\
## Context

No changelog section here.

## Acceptance Criteria
- [ ] Done
"""

BODY_EMPTY_DRAFT = """\
## Changelog Entry Draft

No sub-sections at all.
"""

# ---------------------------------------------------------------------------
# Scenario 1 — Happy Path
# ---------------------------------------------------------------------------


def test_consolidates_all_categories_from_single_task():
    task = make_task(body=BODY_FULL)

    result = ChangelogConsolidator().consolidate([task])

    assert result.added == ["Feature A", "Feature B"]
    assert result.changed == ["Updated config"]
    assert result.fixed == ["Fixed crash"]
    assert result.removed == ["Deprecated endpoint"]


def test_consolidates_entries_from_multiple_tasks():
    task1 = make_task(1, body=BODY_FULL)
    task2 = make_task(2, body=BODY_PARTIAL)

    result = ChangelogConsolidator().consolidate([task1, task2])

    assert result.added == ["Feature A", "Feature B", "Only addition"]
    assert result.changed == ["Updated config"]
    assert result.fixed == ["Fixed crash"]
    assert result.removed == ["Deprecated endpoint"]


def test_returns_changelog_release_draft_instance():
    task = make_task(body=BODY_PARTIAL)

    result = ChangelogConsolidator().consolidate([task])

    assert isinstance(result, ChangelogReleaseDraft)


# ---------------------------------------------------------------------------
# Scenario 2 — Edge Case: partial or missing categories
# ---------------------------------------------------------------------------


def test_handles_task_with_only_some_categories():
    task = make_task(body=BODY_PARTIAL)

    result = ChangelogConsolidator().consolidate([task])

    assert result.added == ["Only addition"]
    assert result.changed == []
    assert result.fixed == []
    assert result.removed == []


def test_handles_task_with_changed_and_fixed_only():
    task = make_task(body=BODY_CHANGED_AND_FIXED_ONLY)

    result = ChangelogConsolidator().consolidate([task])

    assert result.added == []
    assert result.changed == ["Refactored pipeline"]
    assert result.fixed == ["Null pointer in serializer"]
    assert result.removed == []


def test_returns_empty_draft_for_empty_task_list():
    result = ChangelogConsolidator().consolidate([])

    assert result.added == []
    assert result.changed == []
    assert result.fixed == []
    assert result.removed == []


def test_handles_draft_section_with_no_bullet_items():
    task = make_task(body=BODY_EMPTY_DRAFT)

    result = ChangelogConsolidator().consolidate([task])

    assert result.added == []
    assert result.changed == []
    assert result.fixed == []
    assert result.removed == []


# ---------------------------------------------------------------------------
# Scenario 3 — Failure Case: missing or malformed draft section
# ---------------------------------------------------------------------------


def test_raises_when_task_has_no_changelog_draft_section():
    task = make_task(number=99, title="Missing draft", body=BODY_NO_DRAFT)

    with pytest.raises(ChangelogDraftParseError, match="does not contain"):
        ChangelogConsolidator().consolidate([task])


def test_error_message_includes_task_number_and_title():
    task = make_task(number=42, title="My task", body=BODY_NO_DRAFT)

    with pytest.raises(ChangelogDraftParseError, match="#42") as exc_info:
        ChangelogConsolidator().consolidate([task])

    assert "My task" in str(exc_info.value)


def test_raises_on_first_invalid_task_in_list():
    valid = make_task(1, body=BODY_PARTIAL)
    invalid = make_task(2, body=BODY_NO_DRAFT)

    with pytest.raises(ChangelogDraftParseError):
        ChangelogConsolidator().consolidate([valid, invalid])
