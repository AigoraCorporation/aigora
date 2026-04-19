#!/usr/bin/env python3
"""Demo script to show changelog generation with real AI or fallback."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent import ChangelogAgent, CommitInfo
from src.parser import GitCommitReader


async def demo_with_ai():
    """Demonstrate changelog generation with real AI agent (requires API key)."""
    repo = Path("/home/pingu/github/aigora")
    
    print(f"📍 Current repository: {repo}")
    
    # Check for API key
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("\n❌ Error: OPENAI_API_KEY environment variable not set")
        print("\n💡 Please set your API key:")
        print("   export OPENAI_API_KEY=sk-proj-...")
        print("\nOr pass it to this script:")
        print("   OPENAI_API_KEY=sk-proj-... python3 demo_ai.py")
        sys.exit(1)
    
    print(f"🔑 Using LLM (OpenAI GPT-4o-mini) for intelligent changelog summarization")
    print(f"   API Key: {api_key[:20]}...\n")
    
    # Read commits since last tag
    reader = GitCommitReader(str(repo))
    last_tag = reader.get_last_tag()
    
    print(f"🏷️  Last tag: {last_tag}")
    
    if last_tag:
        rev_range = f"{last_tag}..HEAD"
    else:
        rev_range = "HEAD"
    
    commits = reader.get_commits(rev_range)
    
    print(f"📊 Commits since {last_tag}: {len(commits)} total\n")
    print(f"{'─' * 70}\n")
    
    try:
        # Initialize agent and generate changelog with AI
        # Pass the API key directly to avoid environment variable issues
        agent = ChangelogAgent(
            model="gpt-4o-mini",
            repo_path=str(repo),
            api_key=api_key,
        )
        
        print("🤖 Generating changelog with AI analysis...")
        print("   (This will consolidate and intelligently summarize commits)\n")
        
        changelog = await agent.generate_changelog(
            version="v0.2.0",
            rev_range=rev_range,
            date=None,
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
        print("\n💡 This typically means the API key isn't configured correctly.")
        print("   The script needs OPENAI_API_KEY set in the environment.")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(demo_with_ai())
