#!/usr/bin/env python3
"""Demo script to show changelog dry-run without requiring API keys."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import ChangelogAgent, CommitInfo
from src.parser import GitCommitReader


def demo_dryrun():
    """Demonstrate changelog generation dry-run."""
    repo = Path("/home/pingu/github/aigora")
    
    # Read commits since last tag
    reader = GitCommitReader(str(repo))
    last_tag = reader.get_last_tag()
    
    print(f"📍 Current repository: {repo}")
    print(f"🏷️  Last tag: {last_tag}\n")
    
    # Get commits since last tag
    if last_tag:
        rev_range = f"{last_tag}..HEAD"
    else:
        rev_range = "HEAD"
    
    commits = reader.get_commits(rev_range)
    
    print(f"📊 Commits since {last_tag}:\n")
    for i, commit in enumerate(commits, 1):
        breaking = " 🚨 [BREAKING]" if commit.breaking else ""
        scope = f"({commit.scope})" if commit.scope else ""
        print(f"  {i}. {commit.type}{scope}: {commit.subject}{breaking}")
        if commit.body:
            print(f"     └─ {commit.body[:60]}...")
    
    print(f"\n{'─' * 70}\n")
    
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
    
    # Generate fallback changelog (without requiring API keys)
    from unittest.mock import MagicMock, patch
    
    with patch("src.agent.Agent"):
        agent = ChangelogAgent(repo_path=str(repo))
        changelog = agent._generate_fallback_changelog("v0.2.0", commit_infos)
        
        # Format and display
        formatted = agent.format_changelog_entry(changelog)
        
        print("📝 DRY-RUN PREVIEW: Changelog for v0.2.0")
        print("=" * 70)
        print(formatted)
        print("=" * 70)
        print("\n✓ Dry-run mode: CHANGELOG.md was NOT modified")
        print(f"📌 To apply: python -m src.agent --version v0.2.0 \\")
        print(f"             --rev-range {rev_range} \\")
        print(f"             --repo {repo}")


if __name__ == "__main__":
    demo_dryrun()
