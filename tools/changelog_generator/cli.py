#!/usr/bin/env python3
"""
Unified CLI for changelog generation with deterministic and AI-powered modes.

Usage:
    # Deterministic mode (no API key needed, fast preview)
    python3 cli.py --mode deterministic --version v0.2.0

    # AI-powered mode (requires API key, intelligent summaries)
    python3 cli.py --mode ai --version v0.2.0

    # Compare dev against main
    python3 cli.py --mode ai --version v0.2.0 --rev-range main..dev

    # Auto-detect version from last tag
    python3 cli.py --mode deterministic --version auto

    # Output as single-line summary
    python3 cli.py --mode deterministic --version auto --format summary

    # Use specific provider
    python3 cli.py --mode ai --version v0.2.0 --provider anthropic --model claude-3-5-sonnet

    # Specify custom repository and changelog path
    python3 cli.py --mode deterministic --version v0.2.0 --repo /path/to/repo

    # Custom release date
    python3 cli.py --mode ai --version v0.2.0 --date 2026-04-18

    # Documentation scope filter
    python3 cli.py --mode ai --version v0.2.0 --docs-scope curriculum,architecture
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

# Add current directory to path so imports work when running directly
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

from agent import ChangelogAgent
from parser import GitCommitReader

# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NO_COMMITS = 2


def load_env_config() -> dict:
    """Load configuration from .env file or environment variables."""
    env_file = Path(__file__).parent / ".env"

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        if value and not value.startswith("your-"):
                            os.environ.setdefault(key.strip(), value.strip())

    return {
        "provider": os.environ.get("CHANGELOG_PROVIDER", "openai"),
        "model": os.environ.get("CHANGELOG_MODEL", "gpt-4o-mini"),
        "api_key": os.environ.get("CHANGELOG_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"),
        "date": os.environ.get("CHANGELOG_DATE"),
        "rev_range": os.environ.get("CHANGELOG_REV_RANGE"),
        "docs_scope": os.environ.get("CHANGELOG_DOCS_SCOPE"),
    }


def resolve_version(version: str, repo: Path) -> str:
    """Resolve 'auto' version to the next patch increment from the last tag."""
    if version != "auto":
        return version

    reader = GitCommitReader(str(repo))
    last_tag = reader.get_last_tag()

    if not last_tag:
        return "v0.1.0"

    # Increment patch: v0.1.1 -> v0.1.2
    parts = last_tag.lstrip("v").split(".")
    if len(parts) == 3:
        try:
            parts[2] = str(int(parts[2]) + 1)
            return "v" + ".".join(parts)
        except ValueError:
            pass

    return last_tag


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate CHANGELOG.md with deterministic or AI-powered modes",
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        required=True,
        help="Version identifier (e.g., v0.2.0) or 'auto' to increment from last tag",
    )

    parser.add_argument(
        "--mode",
        choices=["deterministic", "ai"],
        default="deterministic",
        help="Generation mode: 'deterministic' (fast, no API key) or 'ai' (requires API key) [default: deterministic]",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only, do not update CHANGELOG.md",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "summary", "json"],
        default="markdown",
        help="Output format: 'markdown' (full), 'summary' (single line), 'json' (machine-readable) [default: markdown]",
    )

    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).parent.parent.parent,
        help="Git repository path [default: repository root]",
    )

    parser.add_argument(
        "--rev-range",
        help="Git revision range (e.g., 'main..dev', 'v0.1.0..HEAD') [default: commits since last tag]",
    )

    parser.add_argument(
        "--date",
        help="Release date in YYYY-MM-DD format [default: today]",
    )

    parser.add_argument(
        "--docs-scope",
        help="Documentation scope filter, comma-separated (e.g., 'curriculum,architecture')",
    )

    parser.add_argument(
        "--provider",
        default="openai",
        help="LLM provider: 'openai' or 'anthropic' [default: openai]",
    )

    parser.add_argument(
        "--model",
        help="LLM model name (e.g., 'gpt-4o-mini', 'claude-3-5-sonnet') [default: from .env or gpt-4o-mini]",
    )

    parser.add_argument(
        "--api-key",
        help="API key for LLM provider [default: from CHANGELOG_API_KEY or provider environment variable]",
    )

    return parser.parse_args()


def format_output(agent: ChangelogAgent, changelog, output_format: str) -> str:
    """Format changelog output according to the requested format."""
    if output_format == "summary":
        total = sum(len(entries) for entries in changelog.sections.values())
        section_counts = [
            f"{len(entries)} {name.lower()}"
            for name, entries in changelog.sections.items()
            if entries
        ]
        return f"{changelog.version}: {total} entries ({', '.join(section_counts)})"

    if output_format == "json":
        import json
        data = {
            "version": changelog.version,
            "date": changelog.date,
            "summary": changelog.summary,
            "sections": {
                name: entries
                for name, entries in changelog.sections.items()
                if entries
            },
        }
        return json.dumps(data, indent=2)

    # Default: markdown
    return agent.format_changelog_entry(changelog)


async def generate_ai_changelog(
    version: str,
    repo: Path,
    rev_range: Optional[str],
    provider: str,
    model: str,
    api_key: str,
    date: Optional[str],
    docs_scope: Optional[str],
    dry_run: bool = False,
    output_format: str = "markdown",
) -> None:
    """Generate changelog using AI-powered mode."""

    if not api_key:
        print("Error: API key not found", file=sys.stderr)
        print("Set CHANGELOG_API_KEY or the provider-specific environment variable.", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    reader = GitCommitReader(str(repo))
    last_tag = reader.get_last_tag()

    if not rev_range:
        rev_range = f"{last_tag}..HEAD" if last_tag else "HEAD"

    try:
        commits = reader.get_commits(rev_range)
    except RuntimeError as e:
        if "unknown revision" in str(e) or "not in the working tree" in str(e):
            print(f"Error: revision range '{rev_range}' not found locally.", file=sys.stderr)
            print("Run 'git fetch origin' and retry.", file=sys.stderr)
            sys.exit(EXIT_ERROR)
        raise

    if not commits:
        print(f"No commits found in range '{rev_range}'.")
        sys.exit(EXIT_NO_COMMITS)

    try:
        agent = ChangelogAgent(
            model=model,
            repo_path=str(repo),
            api_key=api_key,
            provider=provider,
        )

        changelog = await agent.generate_changelog(
            version=version,
            rev_range=rev_range,
            docs_scope=docs_scope,
            date=date,
        )

        print(format_output(agent, changelog, output_format))

        if not dry_run:
            agent.update_changelog(changelog)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(EXIT_ERROR)


def generate_deterministic_changelog(
    version: str,
    repo: Path,
    rev_range: Optional[str],
    date: Optional[str],
    docs_scope: Optional[str],
    dry_run: bool = False,
    output_format: str = "markdown",
) -> None:
    """Generate changelog using deterministic mode (no API key needed)."""

    reader = GitCommitReader(str(repo))
    last_tag = reader.get_last_tag()

    if not rev_range:
        rev_range = f"{last_tag}..HEAD" if last_tag else "HEAD"

    try:
        commits = reader.get_commits(rev_range)
    except RuntimeError as e:
        if "unknown revision" in str(e) or "not in the working tree" in str(e):
            print(f"Error: revision range '{rev_range}' not found locally.", file=sys.stderr)
            print("Run 'git fetch origin' and retry.", file=sys.stderr)
            sys.exit(EXIT_ERROR)
        raise

    if not commits:
        print(f"No commits found in range '{rev_range}'.")
        sys.exit(EXIT_NO_COMMITS)

    try:
        from unittest.mock import patch

        commit_infos = [
            type("CommitInfo", (), {
                "hash": c.hash,
                "type": c.type,
                "scope": c.scope,
                "subject": c.subject,
                "breaking": c.breaking,
            })()
            for c in commits
        ]

        with patch("agent.Agent"):
            agent = ChangelogAgent(repo_path=str(repo))
            changelog = agent._generate_fallback_changelog(version, commit_infos, date)

            print(format_output(agent, changelog, output_format))

            if not dry_run:
                agent.update_changelog(changelog)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(EXIT_ERROR)


async def main():
    """Main entry point."""
    args = parse_arguments()

    env_config = load_env_config()

    provider = args.provider or env_config["provider"]
    model = args.model or env_config["model"]
    api_key = args.api_key or env_config["api_key"]
    date = args.date or env_config["date"]
    rev_range = args.rev_range or env_config["rev_range"]
    docs_scope = args.docs_scope or env_config["docs_scope"]

    version = resolve_version(args.version, args.repo)

    if args.mode == "deterministic":
        generate_deterministic_changelog(
            version=version,
            repo=args.repo,
            rev_range=rev_range,
            date=date,
            docs_scope=docs_scope,
            dry_run=args.dry_run,
            output_format=args.format,
        )
    else:
        await generate_ai_changelog(
            version=version,
            repo=args.repo,
            rev_range=rev_range,
            provider=provider,
            model=model,
            api_key=api_key,
            date=date,
            docs_scope=docs_scope,
            dry_run=args.dry_run,
            output_format=args.format,
        )


if __name__ == "__main__":
    asyncio.run(main())
