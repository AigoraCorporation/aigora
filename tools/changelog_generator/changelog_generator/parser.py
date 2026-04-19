"""Parser for conventional commits from git history."""

import re
import subprocess
from typing import Optional

from .models import Commit


class ConventionalCommitParser:
    """Parses git commits following Conventional Commits format."""

    # Pattern: type(scope)?!?: subject
    PATTERN = re.compile(
        r"^(?P<type>feat|fix|docs|refactor|test|perf|build|ci|chore|revert)"
        r"(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$",
        re.MULTILINE,
    )

    @staticmethod
    def parse(message: str, commit_hash: str) -> Optional[Commit]:
        """
        Parse a commit message into a Commit object.

        Args:
            message: Commit message (subject + optional body)
            commit_hash: Git commit hash

        Returns:
            Commit object if message follows Conventional Commits format, None otherwise
        """
        # Split message into subject (first line) and body (rest)
        lines = message.strip().split("\n", 1)
        subject_line = lines[0]
        body = lines[1].strip() if len(lines) > 1 else ""

        match = ConventionalCommitParser.PATTERN.match(subject_line)
        if not match:
            return None

        return Commit(
            hash=commit_hash,
            type=match.group("type"),
            scope=match.group("scope"),
            subject=match.group("subject"),
            body=body,
            breaking=match.group("breaking") is not None,
        )


class GitCommitReader:
    """Reads commits from git repository."""

    def __init__(self, repo_path: str = "."):
        """
        Initialize with repository path.

        Args:
            repo_path: Path to git repository (default: current directory)
        """
        self.repo_path = repo_path

    def _run_git(self, *args: str) -> str:
        """
        Execute a git command and return output.

        Args:
            *args: Arguments to pass to git command

        Returns:
            Command output as string

        Raises:
            RuntimeError: If git command fails
        """
        try:
            result = subprocess.run(
                ["git", "-C", self.repo_path, *args],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr}")

    def get_commits(self, rev_range: str) -> list[Commit]:
        """
        Get commits in the specified revision range.

        Args:
            rev_range: Git revision range (e.g., "v0.1.0..HEAD" or "HEAD")

        Returns:
            List of parsed Commit objects (only conventional commits included)
        """
        try:
            # Format: hash%x00subject%x00body%x1E (record separator)
            log_format = "%H%x00%s%x00%b%x1E"
            output = self._run_git("log", f"--format={log_format}", rev_range)

            commits = []
            for record in output.split("\x1E"):
                if not record.strip():
                    continue

                parts = record.split("\x00")
                if len(parts) >= 2:
                    commit_hash = parts[0].strip()
                    subject = parts[1].strip()
                    body = parts[2].strip() if len(parts) > 2 else ""
                    full_message = f"{subject}\n{body}" if body else subject

                    parsed = ConventionalCommitParser.parse(full_message, commit_hash)
                    if parsed:
                        commits.append(parsed)

            return commits

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to read git commits: {e.stderr}")

    def get_last_tag(self) -> Optional[str]:
        """
        Get the latest version tag.

        Returns:
            Latest tag string or None if no tags exist
        """
        try:
            output = self._run_git("tag", "--sort=-version:refname")
            tags = [t.strip() for t in output.splitlines() if t.strip()]
            return tags[0] if tags else None
        except RuntimeError:
            return None

    def get_commits_since_last_tag(self) -> list[Commit]:
        """
        Get commits since the last version tag.

        Returns:
            List of Commit objects since last tag (or all commits if no tags exist)
        """
        last_tag = self.get_last_tag()
        rev_range = f"{last_tag}..HEAD" if last_tag else "HEAD"
        return self.get_commits(rev_range)
