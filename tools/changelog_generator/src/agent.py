#!/usr/bin/env python3
"""
AI-Powered Changelog Generator using Pydantic AI

Generates intelligent CHANGELOG entries by analyzing commits and documentation scope
using Claude/GPT models with structured output validation via Pydantic.

Usage:
    Generate changelog using AI analysis:
    $ python3 tools/changelog_agent.py --version v0.2.0 --model gpt-4o-mini --dry-run

    Update CHANGELOG.md with AI-generated entries:
    $ python3 tools/changelog_agent.py --version v0.2.0 --model gpt-4o-mini

    Use Claude model (default):
    $ python3 tools/changelog_agent.py --version v0.2.0

    Analyze specific commit range:
    $ python3 tools/changelog_agent.py --version v0.2.0 --rev-range v0.1.0..HEAD

Options:
    --version VERSION       Version for changelog entry (required)
    --model MODEL          LLM model: claude-3-5-sonnet (default), gpt-4o-mini, gpt-4o
    --date DATE            Release date (YYYY-MM-DD, defaults to today)
    --changelog PATH       Path to CHANGELOG.md (default: CHANGELOG.md)
    --rev-range RANGE      Git revision range (default: commits since last tag)
    --repo PATH            Git repository path (default: current directory)
    --dry-run              Preview without modifying file
    --docs-scope SCOPE     Documentation scope (e.g., 'curriculum,architecture')

Model Providers:
    Anthropic: claude-3-5-sonnet, claude-3-opus, claude-3-sonnet, claude-3-haiku
    OpenAI: gpt-4o-mini, gpt-4o, gpt-4-turbo
    Requires: ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable

Section Generation:
    The AI agent analyzes commits and docs to generate:
    - Added: New features and capabilities
    - Changed: Modifications, improvements, and refactors
    - Fixed: Bug fixes and corrections
    - Removed: Deprecated and removed features
    - Breaking: Breaking changes (commits with ! marker)

Features:
    ✓ Intelligent entry summarization
    ✓ Context-aware categorization
    ✓ Duplicate detection and removal
    ✓ Documentation scope awareness
    ✓ Breaking change analysis
    ✓ Structured validation with Pydantic

See tools/CHANGELOG_AGENT_README.md for detailed documentation.
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

try:
    from pydantic_ai import Agent
except ImportError:
    print(
        "Error: pydantic-ai is not installed. Install with:",
        file=sys.stderr,
    )
    print("  pip install pydantic-ai", file=sys.stderr)
    sys.exit(1)

from .models import Commit, ChangelogContent
from .parser import ConventionalCommitParser, GitCommitReader


class CommitInfo(BaseModel):
    """Information about a commit (for AI agent)."""

    hash: str
    type: str
    scope: Optional[str] = None
    subject: str
    breaking: bool


class ChangelogAgent:
    """AI-powered changelog generator using Pydantic AI."""

    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        repo_path: str = ".",
    ):
        """
        Initialize the changelog agent.

        Args:
            model: LLM model to use (claude-3-5-sonnet, gpt-4o-mini, etc.)
            repo_path: Path to git repository

        Raises:
            ValueError: If repo_path is not a git repository
        """
        self.model = model
        self.repo_path = Path(repo_path)
        if not (self.repo_path / ".git").exists():
            raise ValueError(f"Not a git repository: {repo_path}")

        # Initialize git reader
        self.git_reader = GitCommitReader(str(self.repo_path))

        # Initialize Pydantic AI agent with result type
        system_prompt = self._get_system_prompt()
        self.agent: Agent[ChangelogContent] = Agent(
            model=model,
            result_type=ChangelogContent,
            system_prompt=system_prompt,
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the changelog agent."""
        return """You are an expert changelog generator. Your task is to analyze git commits 
and create well-structured, human-friendly changelog entries.

Guidelines:
- Group related commits into logical, concise entries
- Remove redundancy and duplication
- Highlight what users need to know, not implementation details
- Use active voice and clear language
- Start entries with verbs when possible
- Scope prefixes should be included when relevant
- Breaking changes must be clearly marked
- Keep entries consistent and readable

Sections:
- Added: New features, capabilities, and functionality
- Changed: Modifications, improvements, refactors, and CI/CD changes
- Fixed: Bug fixes and corrections
- Removed: Deprecated and removed features
- Breaking: Backward-incompatible changes

Return structured changelog content with clear sections."""

    def _get_commits(self, rev_range: str) -> List[CommitInfo]:
        """
        Get commits in the specified revision range.

        Args:
            rev_range: Git revision range (e.g., "v0.1.0..HEAD")

        Returns:
            List of CommitInfo objects
        """
        commits = self.git_reader.get_commits(rev_range)
        return [
            CommitInfo(
                hash=c.hash,
                type=c.type,
                scope=c.scope,
                subject=c.subject,
                breaking=c.breaking,
            )
            for c in commits
        ]

    def _get_commits_since_last_version(self) -> List[CommitInfo]:
        """Get commits since the last version tag."""
        commits = self.git_reader.get_commits_since_last_tag()
        return [
            CommitInfo(
                hash=c.hash,
                type=c.type,
                scope=c.scope,
                subject=c.subject,
                breaking=c.breaking,
            )
            for c in commits
        ]

    async def generate_changelog(
        self,
        version: str,
        rev_range: Optional[str] = None,
        docs_scope: Optional[str] = None,
        date: Optional[str] = None,
    ) -> ChangelogContent:
        """
        Generate changelog using AI analysis.

        Args:
            version: Version identifier
            rev_range: Git revision range (None = commits since last tag)
            docs_scope: Documentation scope (comma-separated modules)
            date: Release date (None = today)

        Returns:
            ChangelogContent with structured sections
        """
        if rev_range is None:
            commits = self._get_commits_since_last_version()
        else:
            commits = self._get_commits(rev_range)

        if not commits:
            return ChangelogContent(
                version=version,
                date=date or datetime.now().strftime("%Y-%m-%d"),
                sections={},
                summary="No changes in this release.",
            )

        # Prepare commit summary for the agent
        commit_text = self._format_commits_for_agent(commits, docs_scope)

        # Call the agent to generate changelog
        prompt = f"""Generate changelog for version {version} based on these commits:

{commit_text}

Requirements:
1. Remove duplicates and consolidate similar entries
2. Group logically by feature/component
3. Be concise but informative
4. Include scope prefixes (e.g., "(tutor)", "(assessment)")
5. Mark breaking changes clearly
6. Return JSON with sections as dict of lists

Provide the changelog content with appropriate sections."""

        try:
            result = await self.agent.run(prompt)
            changelog = result.data
        except Exception as e:
            print(f"Warning: AI generation failed: {e}", file=sys.stderr)
            # Fallback to structured output
            changelog = self._generate_fallback_changelog(version, commits, date)

        # Update date if provided
        if date:
            changelog.date = date

        return changelog

    def _format_commits_for_agent(
        self,
        commits: List[CommitInfo],
        docs_scope: Optional[str] = None,
    ) -> str:
        """Format commits for agent analysis."""
        lines = []
        for commit in commits:
            breaking = " [BREAKING]" if commit.breaking else ""
            scope_str = f"({commit.scope})" if commit.scope else ""
            lines.append(f"- {commit.type}{scope_str}{breaking}: {commit.subject}")

        if docs_scope:
            lines.append(f"\nDocumentation scope: {docs_scope}")

        return "\n".join(lines)

    def _generate_fallback_changelog(
        self,
        version: str,
        commits: List[CommitInfo],
        date: Optional[str] = None,
    ) -> ChangelogContent:
        """Generate changelog without AI when agent fails."""
        sections: Dict[str, List[str]] = {}
        seen: set = set()

        type_to_section = {
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

        for commit in commits:
            key = (commit.type, commit.scope, commit.subject.lower())
            if key in seen:
                continue
            seen.add(key)

            section = type_to_section.get(commit.type, "Changed")
            entry = f"({commit.scope}): {commit.subject}" if commit.scope else commit.subject

            if section not in sections:
                sections[section] = []
            sections[section].append(entry)

            if commit.breaking:
                if "Breaking" not in sections:
                    sections["Breaking"] = []
                sections["Breaking"].append(entry)

        return ChangelogContent(
            version=version,
            date=date or datetime.now().strftime("%Y-%m-%d"),
            sections=sections,
            summary=f"Release {version} with {len(seen)} changes",
        )

    def format_changelog_entry(
        self,
        changelog: ChangelogContent,
    ) -> str:
        """
        Format changelog content as markdown.

        Args:
            changelog: ChangelogContent object

        Returns:
            Formatted markdown string
        """
        return changelog.to_markdown()

    def update_changelog(
        self,
        changelog_content: ChangelogContent,
        changelog_path: str = "CHANGELOG.md",
    ) -> None:
        """
        Update CHANGELOG.md with new entries.

        Args:
            changelog_content: ChangelogContent to insert
            changelog_path: Path to CHANGELOG.md file

        Raises:
            FileNotFoundError: If CHANGELOG.md doesn't exist
        """
        changelog_file = self.repo_path / changelog_path
        if not changelog_file.exists():
            raise FileNotFoundError(f"Changelog file not found: {changelog_path}")

        # Generate new entry
        new_entry = self.format_changelog_entry(changelog_content)

        # Read existing changelog
        content = changelog_file.read_text()

        # Find insertion point (after header, before first version)
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


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate changelog using AI analysis of commits and documentation"
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Version for changelog entry (e.g., v0.2.0)",
    )
    parser.add_argument(
        "--model",
        default="claude-3-5-sonnet-20241022",
        help="LLM model (default: claude-3-5-sonnet, or use gpt-4o-mini)",
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
        help="Git revision range (e.g., v0.1.0..HEAD)",
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Path to git repository",
    )
    parser.add_argument(
        "--docs-scope",
        help="Documentation scope (comma-separated: curriculum,architecture)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changelog without updating file",
    )

    args = parser.parse_args()

    try:
        agent = ChangelogAgent(args.model, args.repo)
        changelog = await agent.generate_changelog(
            args.version,
            args.rev_range,
            args.docs_scope,
            args.date,
        )

        # Print generated changelog entry
        changelog_entry = agent.format_changelog_entry(changelog)
        print(changelog_entry)
        print(f"\n📝 Summary: {changelog.summary}")

        # Update file if not dry-run
        if not args.dry_run:
            agent.update_changelog(changelog, args.changelog)
            print(f"\n✓ Updated {args.changelog}")
        else:
            print(f"\n(Dry-run mode: {args.changelog} was not updated)")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
