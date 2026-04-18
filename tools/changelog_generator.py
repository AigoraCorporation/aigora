#!/usr/bin/env python3
"""
Changelog Generator for AIGORA Project

Generates CHANGELOG.md entries based on conventional commits between versions.
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ConventionalCommit:
    """Represents a conventional commit."""

    # Regex pattern for conventional commits
    PATTERN = re.compile(
        r"^(?P<type>feat|fix|docs|refactor|test|perf|build|ci|chore|revert)"
        r"(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$",
        re.MULTILINE,
    )

    def __init__(
        self,
        commit_hash: str,
        message: str,
        body: str = "",
    ):
        self.commit_hash = commit_hash
        self.message = message
        self.body = body
        self._parse()

    def _parse(self):
        """Parse the commit message for conventional commit format."""
        match = self.PATTERN.match(self.message)
        if match:
            self.type = match.group("type")
            self.breaking = match.group("breaking") is not None
            self.scope = match.group("scope")
            self.subject = match.group("subject")
            self.is_valid = True
        else:
            self.type = None
            self.breaking = False
            self.scope = None
            self.subject = self.message
            self.is_valid = False

    def __repr__(self):
        return f"ConventionalCommit(type={self.type}, subject={self.subject})"


class ChangelogGenerator:
    """Generates changelog entries from conventional commits."""

    # Map commit types to changelog sections
    TYPE_TO_SECTION = {
        "feat": "Added",
        "fix": "Fixed",
        "refactor": "Changed",
        "perf": "Changed",
        "ci": "Changed",
        "build": "Changed",
        "docs": "Changed",
        "test": "Changed",
        "chore": "Changed",
        "revert": "Removed",
    }

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")

    def _run_git(self, *args: str) -> str:
        """Execute a git command and return output."""
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), *args],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {e.stderr}")

    def _get_commits(self, rev_range: str) -> List[ConventionalCommit]:
        """Get commits in the specified revision range."""
        log_format = "%H%x00%s%x00%b%x1E"
        output = self._run_git("log", f"--format={log_format}", rev_range)

        commits = []
        if output:
            for entry in output.split("\x1E"):
                if not entry.strip():
                    continue
                parts = entry.split("\x00")
                if len(parts) >= 2:
                    commit_hash = parts[0].strip()
                    subject = parts[1].strip()
                    body = parts[2].strip() if len(parts) > 2 else ""
                    commits.append(ConventionalCommit(commit_hash, subject, body))

        return commits

    def _get_latest_version(self) -> str:
        """Get the latest version tag."""
        try:
            output = self._run_git(
                "describe",
                "--tags",
                "--abbrev=0",
            )
            return output if output else None
        except RuntimeError:
            # No tags found
            return None

    def _get_commits_since_last_version(self) -> List[ConventionalCommit]:
        """Get commits since the last version tag."""
        latest_version = self._get_latest_version()
        if latest_version:
            rev_range = f"{latest_version}..HEAD"
        else:
            # If no tags exist, get all commits
            rev_range = "HEAD"

        return self._get_commits(rev_range)

    def generate_entries(
        self, rev_range: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """Generate changelog entries for commits in the revision range."""
        if rev_range is None:
            commits = self._get_commits_since_last_version()
        else:
            commits = self._get_commits(rev_range)

        # Group commits by section
        sections: Dict[str, List[str]] = {
            "Breaking": [],
            "Added": [],
            "Changed": [],
            "Fixed": [],
            "Removed": [],
        }

        for commit in commits:
            if not commit.is_valid:
                # Skip non-conventional commits
                continue

            # Add to sections based on type
            section = self.TYPE_TO_SECTION.get(commit.type, "Changed")
            entry = f"- {commit.subject}"
            if commit.scope:
                entry = f"- ({commit.scope}): {commit.subject}"

            sections[section].append(entry)

            # Add to Breaking section if it's a breaking change
            if commit.breaking:
                breaking_entry = f"- {commit.subject} ({commit.type}({commit.scope or 'core'})!)"
                if breaking_entry not in sections["Breaking"]:
                    sections["Breaking"].append(breaking_entry)

        # Remove empty sections
        return {k: v for k, v in sections.items() if v}

    def format_changelog_entry(
        self,
        version: str,
        date: Optional[str] = None,
        entries: Optional[Dict[str, List[str]]] = None,
    ) -> str:
        """Format a changelog entry in the standard format."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if entries is None:
            entries = self.generate_entries()

        lines = [f"## [{version}] - {date}\n"]

        for section in ["Breaking", "Added", "Changed", "Fixed", "Removed"]:
            if section in entries and entries[section]:
                lines.append(f"### {section}")
                for entry in entries[section]:
                    lines.append(entry)
                lines.append("")

        return "\n".join(lines)

    def update_changelog(
        self,
        version: str,
        changelog_path: str = "CHANGELOG.md",
        date: Optional[str] = None,
        entries: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        """Update CHANGELOG.md with new entries."""
        changelog_file = self.repo_path / changelog_path
        if not changelog_file.exists():
            raise FileNotFoundError(f"Changelog file not found: {changelog_path}")

        # Generate new entry
        new_entry = self.format_changelog_entry(version, date, entries)

        # Read existing changelog
        content = changelog_file.read_text()

        # Find the insertion point (after the header and first separator)
        # Look for the first "## [v..." line
        lines = content.split("\n")
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("## ["):
                insert_idx = i
                break

        # Insert new entry
        new_lines = lines[:insert_idx] + [new_entry] + ["---", ""] + lines[insert_idx:]
        new_content = "\n".join(new_lines)

        changelog_file.write_text(new_content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate changelog entries from conventional commits"
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Version for the changelog entry (e.g., v0.2.0)",
    )
    parser.add_argument(
        "--date",
        help="Release date (YYYY-MM-DD, defaults to today)",
    )
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="Path to CHANGELOG.md file",
    )
    parser.add_argument(
        "--rev-range",
        help="Git revision range (e.g., v0.1.0..HEAD). Defaults to commits since last tag.",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to git repository",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print changelog entry without updating file",
    )

    args = parser.parse_args()

    try:
        generator = ChangelogGenerator(args.repo)
        entries = generator.generate_entries(args.rev_range)

        # Print generated changelog entry
        changelog_entry = generator.format_changelog_entry(
            args.version,
            args.date,
            entries,
        )
        print(changelog_entry)

        # Update file if not dry-run
        if not args.dry_run:
            generator.update_changelog(
                args.version,
                args.changelog,
                args.date,
                entries,
            )
            print(f"\n✓ Updated {args.changelog}")
        else:
            print(f"\n(Dry-run mode: {args.changelog} was not updated)")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
