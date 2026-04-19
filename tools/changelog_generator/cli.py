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

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import ChangelogAgent
from src.parser import GitCommitReader


def load_env_config() -> dict:
    """Load configuration from .env file or environment variables."""
    env_file = Path(__file__).parent / ".env"
    
    # Load .env file if it exists
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        if value and not value.startswith("your-"):
                            os.environ.setdefault(key.strip(), value.strip())
    
    # Return configuration from environment
    return {
        "provider": os.environ.get("CHANGELOG_PROVIDER", "openai"),
        "model": os.environ.get("CHANGELOG_MODEL", "gpt-4o-mini"),
        "api_key": os.environ.get("CHANGELOG_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"),
        "date": os.environ.get("CHANGELOG_DATE"),
        "rev_range": os.environ.get("CHANGELOG_REV_RANGE"),
        "docs_scope": os.environ.get("CHANGELOG_DOCS_SCOPE"),
    }


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate CHANGELOG.md with deterministic or AI-powered modes",
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    # Required arguments
    parser.add_argument(
        "--version",
        required=True,
        help="Version identifier for changelog entry (e.g., v0.2.0)",
    )
    
    # Mode selection
    parser.add_argument(
        "--mode",
        choices=["deterministic", "ai"],
        default="deterministic",
        help="Generation mode: 'deterministic' (fast, no API key) or 'ai' (intelligent, requires API key) [default: deterministic]",
    )
    
    # Optional arguments
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).parent.parent.parent,  # Default to repo root
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
    
    # AI-specific arguments
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
        help="API key for LLM provider [default: from CHANGELOG_API_KEY or OPENAI_API_KEY environment variables]",
    )
    
    return parser.parse_args()


async def generate_ai_changelog(
    version: str,
    repo: Path,
    rev_range: Optional[str],
    provider: str,
    model: str,
    api_key: str,
    date: Optional[str],
    docs_scope: Optional[str],
) -> None:
    """Generate changelog using AI-powered mode."""
    
    print(f"📍 Current repository: {repo}")
    
    if not api_key:
        print(f"\n❌ Error: API key not found")
        print(f"\n💡 Set one of these environment variables or in .env file:")
        if provider == "openai":
            print(f"   OPENAI_API_KEY=sk-proj-...")
            print(f"   CHANGELOG_API_KEY=sk-proj-...")
        elif provider == "anthropic":
            print(f"   ANTHROPIC_API_KEY=sk-ant-...")
            print(f"   CHANGELOG_API_KEY=sk-ant-...")
        else:
            print(f"   CHANGELOG_API_KEY=your-key")
        sys.exit(1)
    
    print(f"🔑 Using {provider} provider: {model}")
    print(f"   API Key: {api_key[:20]}...\n")
    
    # Read commits
    reader = GitCommitReader(str(repo))
    last_tag = reader.get_last_tag()
    
    print(f"🏷️  Last tag: {last_tag or 'None'}")
    
    if not rev_range:
        rev_range = f"{last_tag}..HEAD" if last_tag else "HEAD"
    
    commits = reader.get_commits(rev_range)
    
    print(f"📊 Commits in range: {len(commits)} total\n")
    print(f"{'─' * 70}\n")
    
    try:
        # Initialize agent
        agent = ChangelogAgent(
            model=model,
            repo_path=str(repo),
            api_key=api_key,
            provider=provider,
        )
        
        print("🤖 Generating changelog with AI analysis...")
        print("   (This will consolidate and intelligently summarize commits)\n")
        
        changelog = await agent.generate_changelog(
            version=version,
            rev_range=rev_range,
            docs_scope=docs_scope,
            date=date,
        )
        
        # Format and display
        formatted = agent.format_changelog_entry(changelog)
        
        print("📝 AI-POWERED CHANGELOG")
        print("=" * 70)
        print(formatted)
        print("=" * 70)
        print(f"\n✓ Summary: {changelog.summary}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print(f"   1. Check that API key is valid")
        print(f"   2. Verify provider '{provider}' is correct")
        print(f"   3. Ensure model '{model}' is available")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def generate_deterministic_changelog(
    version: str,
    repo: Path,
    rev_range: Optional[str],
    date: Optional[str],
    docs_scope: Optional[str],
) -> None:
    """Generate changelog using deterministic mode (no API key needed)."""
    
    print(f"📍 Current repository: {repo}")
    
    # Read commits
    reader = GitCommitReader(str(repo))
    last_tag = reader.get_last_tag()
    
    print(f"🏷️  Last tag: {last_tag or 'None'}")
    
    if not rev_range:
        rev_range = f"{last_tag}..HEAD" if last_tag else "HEAD"
    
    commits = reader.get_commits(rev_range)
    
    print(f"📊 Commits in range: {len(commits)} total\n")
    
    # Show commit list
    print("Commits to be grouped:")
    for i, commit in enumerate(commits, 1):
        breaking = " 🚨 [BREAKING]" if commit.breaking else ""
        scope = f"({commit.scope})" if commit.scope else ""
        print(f"  {i:2}. {commit.type}{scope}: {commit.subject}{breaking}")
    
    print(f"\n{'─' * 70}\n")
    
    try:
        from src.agent import CommitInfo
        
        # Convert to CommitInfo for agent
        commit_infos = [
            CommitInfo(
                hash=c.hash,
                type=c.type,
                scope=c.scope,
                subject=c.subject,
                breaking=c.breaking,
            )
            for c in commits
        ]
        
        # Generate fallback changelog (no API needed)
        from unittest.mock import patch
        
        with patch("src.agent.Agent"):
            agent = ChangelogAgent(repo_path=str(repo))
            changelog = agent._generate_fallback_changelog(version, commit_infos, date)
            
            # Format and display
            formatted = agent.format_changelog_entry(changelog)
            
            print("📝 DETERMINISTIC CHANGELOG")
            print("=" * 70)
            print(formatted)
            print("=" * 70)
            print(f"\n✓ Summary: {changelog.summary}")
            print("\n✨ Deterministic mode: No API key needed, fast preview")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Load environment config and merge with arguments
    env_config = load_env_config()
    
    # Use argument if provided, otherwise use environment
    provider = args.provider or env_config["provider"]
    model = args.model or env_config["model"]
    api_key = args.api_key or env_config["api_key"]
    date = args.date or env_config["date"]
    rev_range = args.rev_range or env_config["rev_range"]
    docs_scope = args.docs_scope or env_config["docs_scope"]
    
    if args.mode == "deterministic":
        generate_deterministic_changelog(
            version=args.version,
            repo=args.repo,
            rev_range=rev_range,
            date=date,
            docs_scope=docs_scope,
        )
    else:  # ai mode
        await generate_ai_changelog(
            version=args.version,
            repo=args.repo,
            rev_range=rev_range,
            provider=provider,
            model=model,
            api_key=api_key,
            date=date,
            docs_scope=docs_scope,
        )


if __name__ == "__main__":
    asyncio.run(main())
