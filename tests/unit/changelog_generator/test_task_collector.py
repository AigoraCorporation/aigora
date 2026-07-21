from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from changelog_generator.release_detector import ReleaseMetadata
from changelog_generator.task_collector import (
    ReleaseTask,
    TaskCollectionError,
    TaskCollector,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_release(name: str = "Curriculum Graph API Foundation") -> ReleaseMetadata:
    return ReleaseMetadata(
        version="v0.2.2",
        name=name,
        planned_date="2026-06-15",
        status="🚧 In Progress",
        details_url="https://example.com/186",
    )


def make_milestone(number: int = 5, title: str = "Curriculum Graph API Foundation") -> dict:
    return {"number": number, "title": title}


def make_issue(
    number: int = 42,
    title: str = "Add feature X",
    labels: list[str] | None = None,
    milestone_title: str = "Curriculum Graph API Foundation",
) -> dict:
    return {
        "number": number,
        "title": title,
        "body": "## Changelog Entry Draft\n\n### Added\n- Feature X\n",
        "state": "open",
        "labels": [{"name": lbl} for lbl in (labels or ["release"])],
        "milestone": {"title": milestone_title},
    }


def _make_fake_urlopen(responses: list[list[dict]]):
    """Returns a fake urlopen that yields successive JSON payloads."""
    call_count = 0

    def fake_urlopen(req, timeout=None):
        nonlocal call_count
        if call_count >= len(responses):
            raise AssertionError(
                f"Unexpected HTTP call #{call_count + 1}. "
                f"Only {len(responses)} response(s) were provided."
            )
        data = json.dumps(responses[call_count]).encode("utf-8")
        call_count += 1

        mock_response = MagicMock()
        mock_response.read.return_value = data
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        return mock_response

    return fake_urlopen


def make_collector() -> TaskCollector:
    return TaskCollector(token="fake-token", owner="AigoraCorporation", repo="aigora")


# ---------------------------------------------------------------------------
# Scenario 1 — Happy Path
# ---------------------------------------------------------------------------


def test_collects_tasks_matching_label_and_milestone():
    milestones = [make_milestone()]
    issues = [make_issue()]

    with patch("urllib.request.urlopen", side_effect=_make_fake_urlopen([milestones, issues, []])):
        result = make_collector().collect(make_release())

    assert len(result) == 1
    assert result[0].number == 42
    assert result[0].title == "Add feature X"
    assert "release" in result[0].labels
    assert result[0].milestone == "Curriculum Graph API Foundation"


def test_returned_task_contains_all_required_fields():
    milestones = [make_milestone()]
    issues = [make_issue(number=7, title="Fix crash")]

    with patch("urllib.request.urlopen", side_effect=_make_fake_urlopen([milestones, issues, []])):
        result = make_collector().collect(make_release())

    task = result[0]
    assert isinstance(task, ReleaseTask)
    assert task.number == 7
    assert task.title == "Fix crash"
    assert task.state == "open"
    assert "release" in task.labels
    assert task.milestone == "Curriculum Graph API Foundation"


# ---------------------------------------------------------------------------
# Scenario 2 — Edge Case: partial matches are excluded
# ---------------------------------------------------------------------------


def test_only_issues_matching_both_criteria_are_returned():
    """GitHub API is queried with both milestone and label filters.

    The API itself enforces both filters, so an empty response means
    no double-matching issues exist.
    """
    milestones = [make_milestone()]
    issues = []  # API returns nothing when both filters applied and nothing matches

    with patch("urllib.request.urlopen", side_effect=_make_fake_urlopen([milestones, issues])):
        result = make_collector().collect(make_release())

    assert result == []


def test_returns_empty_list_when_no_issues_match():
    milestones = [make_milestone()]
    issues = []

    with patch("urllib.request.urlopen", side_effect=_make_fake_urlopen([milestones, issues])):
        result = make_collector().collect(make_release())

    assert result == []


def test_pagination_collects_all_milestones_across_pages():
    """Verify milestone pagination works when target is on page 2."""
    milestones_page1 = [make_milestone(number=1, title="Other Release")]
    milestones_page2 = [make_milestone(number=5, title="Curriculum Graph API Foundation")]
    issues = [make_issue()]

    with patch("urllib.request.urlopen", side_effect=_make_fake_urlopen([milestones_page1, milestones_page2, issues, []])):
        result = make_collector().collect(make_release())

    assert len(result) == 1
    assert result[0].number == 42


def test_pagination_collects_all_issues_across_pages():
    """Verify issue pagination works when there are multiple pages."""
    milestones = [make_milestone()]
    issues_page1 = [make_issue(number=1, title="Task 1")]
    issues_page2 = [make_issue(number=2, title="Task 2")]

    with patch("urllib.request.urlopen", side_effect=_make_fake_urlopen([milestones, issues_page1, issues_page2, []])):
        result = make_collector().collect(make_release())

    assert len(result) == 2
    assert result[0].number == 1
    assert result[1].number == 2


# ---------------------------------------------------------------------------
# Scenario 3 — Failure Cases
# ---------------------------------------------------------------------------


def test_raises_when_milestone_not_found():
    milestones: list[dict] = []

    with patch("urllib.request.urlopen", side_effect=_make_fake_urlopen([milestones])):
        with pytest.raises(TaskCollectionError, match="No GitHub milestone found"):
            make_collector().collect(make_release())


def test_raises_when_github_api_returns_http_error():
    import urllib.error

    http_error = urllib.error.HTTPError(
        url="https://api.github.com/repos/org/repo/milestones",
        code=401,
        msg="Unauthorized",
        hdrs=MagicMock(),
        fp=None,
    )

    with patch("urllib.request.urlopen", side_effect=http_error):
        with pytest.raises(TaskCollectionError, match=r"GitHub API request failed \[401\]"):
            make_collector().collect(make_release())


def test_raises_when_github_api_is_unreachable():
    import urllib.error

    url_error = urllib.error.URLError(reason="Name or service not known")

    with patch("urllib.request.urlopen", side_effect=url_error):
        with pytest.raises(TaskCollectionError, match="GitHub API connection error"):
            make_collector().collect(make_release())


def test_timeout_parameter_is_passed_to_urlopen():
    """Verify that the timeout parameter is correctly passed to urlopen."""
    milestones = [make_milestone()]
    issues = [make_issue()]
    responses = [milestones, issues, []]

    captured_timeout = []
    call_count = 0

    def fake_urlopen_with_timeout_capture(req, timeout=None):
        nonlocal call_count
        captured_timeout.append(timeout)
        if call_count >= len(responses):
            raise AssertionError(
                f"Unexpected HTTP call #{call_count + 1}. "
                f"Only {len(responses)} response(s) were provided."
            )
        data = json.dumps(responses[call_count]).encode("utf-8")
        call_count += 1

        mock_response = MagicMock()
        mock_response.read.return_value = data
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        return mock_response

    with patch("urllib.request.urlopen", side_effect=fake_urlopen_with_timeout_capture):
        collector = TaskCollector(token="fake-token", owner="AigoraCorporation", repo="aigora", timeout=15.5)
        collector.collect(make_release())

    # Should have made 3 calls: milestones page 1, issues page 1, issues page 2 (empty terminator)
    assert len(captured_timeout) == 3
    assert all(t == 15.5 for t in captured_timeout)


# ---------------------------------------------------------------------------
# Scenario 4 — Pull-request filtering
# ---------------------------------------------------------------------------


def test_pull_requests_are_excluded_from_results():
    """Verify that items with a pull_request key are filtered out of collected tasks."""
    milestones = [make_milestone()]
    pr_item = {**make_issue(number=99, title="A PR"), "pull_request": {"url": "..."}}
    regular = make_issue(number=42, title="A real issue")

    with patch(
        "urllib.request.urlopen",
        side_effect=_make_fake_urlopen([milestones, [pr_item, regular], []]),
    ):
        result = make_collector().collect(make_release())

    assert len(result) == 1
    assert result[0].number == 42


# ---------------------------------------------------------------------------
# Scenario 5 — Fake urlopen guard
# ---------------------------------------------------------------------------


def test_fake_urlopen_raises_assertion_error_when_over_called():
    fake = _make_fake_urlopen([[make_milestone()]])
    fake(MagicMock())  # first call: OK

    with pytest.raises(AssertionError, match="Unexpected HTTP call"):
        fake(MagicMock())
