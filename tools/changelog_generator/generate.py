#!/usr/bin/env python
"""Changelog generation script.

Reads the current release from README.md, collects release tasks from GitHub,
consolidates their changelog draft sections, and updates CHANGELOG.md.

Usage:
    python tools/changelog_generator/generate.py

Required environment variable:
    GITHUB_TOKEN         GitHub token with repo read access

Optional environment variables:
    README_PATH          Path to README.md (default: README.md)
    CHANGELOG_PATH       Path to CHANGELOG.md (default: CHANGELOG.md)
    GITHUB_REPO_OWNER    Repository owner (default: AigoraCorporation)
    GITHUB_REPO_NAME     Repository name (default: aigora)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure tools/ is on sys.path when this script is run directly.
sys.path.insert(0, str(Path(__file__).parent.parent))

from changelog_generator.changelog_consolidator import (  # noqa: E402
    ChangelogConsolidator,
    ChangelogDraftParseError,
)
from changelog_generator.changelog_writer import ChangelogWriter  # noqa: E402
from changelog_generator.release_detector import (  # noqa: E402
    ReleaseDetectionError,
    ReleaseDetector,
)
from changelog_generator.task_collector import (  # noqa: E402
    TaskCollectionError,
    TaskCollector,
)


def main() -> None:
    readme_path = Path(os.environ.get("README_PATH", "README.md"))
    changelog_path = Path(os.environ.get("CHANGELOG_PATH", "CHANGELOG.md"))
    github_token = os.environ.get("GITHUB_TOKEN")
    owner = os.environ.get("GITHUB_REPO_OWNER", "AigoraCorporation")
    repo = os.environ.get("GITHUB_REPO_NAME", "aigora")

    if not github_token:
        sys.exit("Error: GITHUB_TOKEN environment variable is required.")

    # Step 1: detect current release from README
    try:
        release = ReleaseDetector().detect(readme_path)
    except ReleaseDetectionError as exc:
        sys.exit(f"Release detection failed: {exc}")

    print(f"Detected release: {release.version} — {release.name}")

    # Step 2: collect release tasks from GitHub
    try:
        tasks = TaskCollector(token=github_token, owner=owner, repo=repo).collect(release)
    except TaskCollectionError as exc:
        sys.exit(f"Task collection failed: {exc}")

    if not tasks:
        sys.exit(
            f"No release tasks found for milestone '{release.name}' with label 'release'. "
            "Changelog not generated."
        )

    print(f"Collected {len(tasks)} release task(s).")

    # Step 3: consolidate changelog draft sections
    try:
        draft = ChangelogConsolidator().consolidate(tasks)
    except ChangelogDraftParseError as exc:
        sys.exit(f"Changelog draft consolidation failed: {exc}")

    # Step 4: render and write changelog
    try:
        writer = ChangelogWriter()
        entry = writer.render(release, draft)
        writer.prepend_to_changelog(entry, changelog_path)
    except OSError as exc:
        sys.exit(f"Failed to write CHANGELOG.md: {exc}")

    print(f"CHANGELOG.md updated for {release.version}.")


if __name__ == "__main__":
    main()
