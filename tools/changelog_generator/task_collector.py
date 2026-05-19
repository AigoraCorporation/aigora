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
        milestones = self._get_paginated(
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
        return [self._map_task(issue) for issue in self._get_paginated(path)]

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

    def _get_paginated(self, path: str) -> list[dict]:
        """Fetch all pages of results from a GitHub API endpoint.
        
        Follows the Link header to retrieve all pages until no 'next' link is present.
        
        Args:
            path: The API endpoint path (e.g., "/repos/owner/repo/milestones?per_page=100")
        
        Returns:
            A list of dictionaries representing GitHub API resources (milestones or issues).
        
        Raises:
            TaskCollectionError: If the API request fails due to HTTP errors or connection issues.
        """
        results = []
        current_path = path
        
        while current_path:
            url = f"{self._GITHUB_API}{current_path}"
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
                    page_data = json.loads(response.read().decode("utf-8"))
                    results.extend(page_data)
                    
                    # Parse Link header for next page
                    link_header = response.headers.get("Link", "")
                    current_path = self._parse_next_link(link_header)
                    
            except urllib.error.HTTPError as exc:
                raise TaskCollectionError(
                    f"GitHub API request failed [{exc.code}] for {url}: {exc.reason}"
                ) from exc
            except urllib.error.URLError as exc:
                raise TaskCollectionError(
                    f"GitHub API connection error for {url}: {exc.reason}"
                ) from exc
        
        return results

    def _parse_next_link(self, link_header: str) -> str | None:
        """Extract the 'next' link path from a GitHub API Link header.
        
        Args:
            link_header: The Link header value from the GitHub API response.
                         An empty string returns None.
        
        Example Link header:
            <https://api.github.com/repos/owner/repo/issues?page=2>; rel="next",
            <https://api.github.com/repos/owner/repo/issues?page=5>; rel="last"
        
        Returns:
            The path portion (e.g., "/repos/owner/repo/issues?page=2") or None if no 'next' link exists.
        """
        if not link_header:
            return None
        
        for link in link_header.split(","):
            parts = link.strip().split(";")
            if len(parts) >= 2:
                url_part = parts[0].strip()
                rel_part = parts[1].strip()
                
                if 'rel="next"' in rel_part:
                    # Extract URL from <...>
                    if url_part.startswith("<") and url_part.endswith(">"):
                        full_url = url_part[1:-1]
                        # Extract path from full URL
                        if self._GITHUB_API in full_url:
                            return full_url.replace(self._GITHUB_API, "")
        
        return None
