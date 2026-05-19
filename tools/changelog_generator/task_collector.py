from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from changelog_generator.release_detector import ReleaseMetadata


@dataclass(frozen=True)
class ReleaseTask:
    number: int
    title: str
    body: str
    state: str
    labels: tuple[str, ...]
    milestone: str


class TaskCollectionError(Exception):
    pass


class TaskCollector:
    """Collects GitHub issues associated with the current release.

    Filters issues that simultaneously:
    - have the 'release' label
    - belong to the milestone whose title matches the current release name
    """

    _GITHUB_API = "https://api.github.com"

    def __init__(self, token: str, owner: str, repo: str) -> None:
        self._token = token
        self._owner = owner
        self._repo = repo

    def collect(self, release: ReleaseMetadata) -> list[ReleaseTask]:
        milestone_number = self._find_milestone_number(release.name)
        if milestone_number is None:
            raise TaskCollectionError(
                f"No GitHub milestone found matching release name: {release.name!r}"
            )
        return self._fetch_tasks(milestone_number)

    def _find_milestone_number(self, name: str) -> int | None:
        milestones = self._get(
            f"/repos/{self._owner}/{self._repo}/milestones?per_page=100&state=all"
        )
        return next(
            (ms["number"] for ms in milestones if ms["title"] == name),
            None,
        )

    def _fetch_tasks(self, milestone_number: int) -> list[ReleaseTask]:
        path = (
            f"/repos/{self._owner}/{self._repo}/issues"
            f"?milestone={milestone_number}&labels=release&state=open&per_page=100"
        )
        return [self._map_task(issue) for issue in self._get(path)]

    def _map_task(self, issue: dict) -> ReleaseTask:
        return ReleaseTask(
            number=issue["number"],
            title=issue["title"],
            body=issue.get("body") or "",
            state=issue["state"],
            labels=tuple(label["name"] for label in issue.get("labels", [])),
            milestone=issue["milestone"]["title"] if issue.get("milestone") else "",
        )

    def _get(self, path: str) -> list[dict]:
        url = f"{self._GITHUB_API}{path}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise TaskCollectionError(
                f"GitHub API request failed [{exc.code}] for {url}: {exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise TaskCollectionError(
                f"GitHub API connection error for {url}: {exc.reason}"
            ) from exc
