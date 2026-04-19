#!/usr/bin/env python3
"""Demo script to show changelog generation with real AI."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import ChangelogAgent, CommitInfo
from src.parser import GitCommitReader


def load_env_config():
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
    
    # Return configuration
    return {
        "provider": os.environ.get("CHANGELOG_PROVIDER", "openai"),
        "model": os.environ.get("CHANGELOG_MODEL", "gpt-4o-mini"),
        "api_key": os.environ.get("CHANGELOG_API_KEY") or os.environ.get("OPENAI_API_KEY"),
        "date": os.environ.get("CHANGELOG_DATE"),
        "rev_range": os.environ.get("CHANGELOG_REV_RANGE"),
        "docs_scope": os.environ.get("CHANGELOG_DOCS_SCOPE"),
    }


async def demo_with_ai():
    """Demonstrate changelog generation with real AI agent."""
    
    # Load configuration
    config = load_env_config()
    provider = config["provider"]
    model = config["model"]
    api_key = config["api_key"]
    
    repo = Path("/home/pingu/github/aigora")
    
    print(f"📍 Current repository: {repo}")
    
    # Check for API key
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
        print(f"\n   Or copy .env.example to .env and fill in your values:")
        print(f"   cp .env.example .env")
        sys.exit(1)
    
    print(f"🔑 Using {provider} provider: {model}")
    print(f"   API Key: {api_key[:20]}...\n")
    
    # Read commits since last tag
    reader = GitCommitReader(str(repo))
    last_tag = reader.get_last_tag()
    
    print(f"🏷️  Last tag: {last_tag}")
    
    rev_range = config["rev_range"]
    if not rev_range:
        rev_range = f"{last_tag}..HEAD" if last_tag else "HEAD"
    
    commits = reader.get_commits(rev_range)
    
    print(f"📊 Commits since {last_tag}: {len(commits)} total\n")
    print(f"{'─' * 70}\n")
    
    try:
        # Initialize agent with configuration
        agent = ChangelogAgent(
            model=model,
            repo_path=str(repo),
            api_key=api_key,
            provider=provider,
        )
        
        print("🤖 Generating changelog with AI analysis...")
        print("   (This will consolidate and intelligently summarize commits)\n")
        
        changelog = await agent.generate_changelog(
            version="v0.2.0",
            rev_range=rev_range,
            docs_scope=config["docs_scope"],
            date=config["date"],
        )
        
        # Format and display
        formatted = agent.format_changelog_entry(changelog)
        
        print("📝 AI-POWERED CHANGELOG for v0.2.0")
        print("=" * 70)
        print(formatted)
        print("=" * 70)
        print(f"\n✓ Summary: {changelog.summary}")
        print(f"📌 To apply: python -m src.agent --version v0.2.0 \\")
        print(f"             --rev-range {rev_range} \\")
        print(f"             --repo {repo}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print(f"   1. Check that API key is valid")
        print(f"   2. Verify provider '{provider}' is correct")
        print(f"   3. Ensure model '{model}' is available")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(demo_with_ai())
