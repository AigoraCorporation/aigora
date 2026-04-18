"""Tests for the models module."""

import sys
from pathlib import Path

import pytest

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import Commit, ChangelogContent, ChangelogSection


class TestCommit:
    """Tests for Commit model."""

    def test_commit_creation(self):
        """Test creating a Commit object."""
        commit = Commit(
            hash="abc123",
            type="feat",
            scope="test",
            subject="add feature",
        )

        assert commit.hash == "abc123"
        assert commit.type == "feat"
        assert commit.scope == "test"
        assert commit.subject == "add feature"
        assert not commit.breaking
        assert commit.body == ""

    def test_commit_with_breaking_change(self):
        """Test commit with breaking change."""
        commit = Commit(
            hash="abc123",
            type="feat",
            scope="api",
            subject="change schema",
            breaking=True,
        )

        assert commit.breaking

    def test_commit_with_body(self):
        """Test commit with body."""
        commit = Commit(
            hash="abc123",
            type="feat",
            scope="test",
            subject="add feature",
            body="This is a detailed description",
        )

        assert "detailed description" in commit.body

    def test_to_conventional_format(self):
        """Test converting to conventional format."""
        commit = Commit(
            hash="abc123",
            type="feat",
            scope="test",
            subject="add feature",
        )

        assert commit.to_conventional_format() == "feat(test): add feature"

    def test_to_conventional_format_breaking(self):
        """Test breaking change format."""
        commit = Commit(
            hash="abc123",
            type="feat",
            scope="api",
            subject="change schema",
            breaking=True,
        )

        assert commit.to_conventional_format() == "feat(api)!: change schema"

    def test_to_conventional_format_no_scope(self):
        """Test format without scope."""
        commit = Commit(
            hash="abc123",
            type="fix",
            scope=None,
            subject="fix bug",
        )

        assert commit.to_conventional_format() == "fix: fix bug"

    def test_commit_validation(self):
        """Test Pydantic validation."""
        # Valid commit
        commit = Commit(
            hash="abc123",
            type="feat",
            scope="test",
            subject="test",
        )
        assert commit is not None

        # Invalid - missing required fields
        with pytest.raises(Exception):  # Pydantic ValidationError
            Commit(hash="abc123", type="feat")


class TestChangelogSection:
    """Tests for ChangelogSection model."""

    def test_section_creation(self):
        """Test creating a section."""
        section = ChangelogSection(
            section="Added",
            entries=["- feature 1", "- feature 2"],
        )

        assert section.section == "Added"
        assert len(section.entries) == 2

    def test_section_is_empty(self):
        """Test empty section check."""
        empty_section = ChangelogSection(section="Added", entries=[])
        non_empty_section = ChangelogSection(section="Added", entries=["- entry"])

        assert empty_section.is_empty()
        assert not non_empty_section.is_empty()

    def test_section_to_markdown(self):
        """Test markdown conversion."""
        section = ChangelogSection(
            section="Added",
            entries=["- feature 1", "- feature 2"],
        )

        markdown = section.to_markdown()

        assert "### Added" in markdown
        assert "- feature 1" in markdown
        assert "- feature 2" in markdown

    def test_empty_section_to_markdown(self):
        """Test empty section returns empty string."""
        section = ChangelogSection(section="Added", entries=[])

        assert section.to_markdown() == ""

    def test_all_section_types(self):
        """Test all valid section types."""
        sections = ["Added", "Changed", "Fixed", "Removed", "Breaking"]

        for section_name in sections:
            section = ChangelogSection(
                section=section_name,
                entries=["- entry"],
            )
            assert section.section == section_name


class TestChangelogContent:
    """Tests for ChangelogContent model."""

    def test_changelog_creation(self):
        """Test creating changelog content."""
        changelog = ChangelogContent(
            version="v0.2.0",
            date="2026-04-18",
            sections={
                "Added": ["- feature 1"],
                "Fixed": ["- bug fix"],
            },
            summary="Release with new features",
        )

        assert changelog.version == "v0.2.0"
        assert changelog.date == "2026-04-18"
        assert len(changelog.sections) == 2

    def test_changelog_default_values(self):
        """Test default values."""
        changelog = ChangelogContent(
            version="v0.1.0",
            date="2026-04-18",
        )

        assert changelog.sections == {}
        assert changelog.summary == ""

    def test_changelog_to_markdown(self):
        """Test markdown conversion."""
        changelog = ChangelogContent(
            version="v0.2.0",
            date="2026-04-18",
            sections={
                "Added": ["- feature 1", "- feature 2"],
                "Fixed": ["- bug 1"],
            },
        )

        markdown = changelog.to_markdown()

        assert "## [v0.2.0] - 2026-04-18" in markdown
        assert "### Added" in markdown
        assert "- feature 1" in markdown
        assert "### Fixed" in markdown
        assert "- bug 1" in markdown

    def test_changelog_section_order(self):
        """Test that sections appear in correct order."""
        changelog = ChangelogContent(
            version="v0.2.0",
            date="2026-04-18",
            sections={
                "Fixed": ["- fix"],
                "Added": ["- feature"],
                "Breaking": ["- breaking"],
                "Changed": ["- change"],
            },
        )

        markdown = changelog.to_markdown()
        breaking_idx = markdown.find("### Breaking")
        added_idx = markdown.find("### Added")
        changed_idx = markdown.find("### Changed")
        fixed_idx = markdown.find("### Fixed")

        assert breaking_idx < added_idx < changed_idx < fixed_idx

    def test_changelog_empty_sections_excluded(self):
        """Test that empty sections are not included."""
        changelog = ChangelogContent(
            version="v0.2.0",
            date="2026-04-18",
            sections={
                "Added": ["- feature"],
                "Changed": [],
                "Fixed": [],
            },
        )

        markdown = changelog.to_markdown()

        assert "### Added" in markdown
        assert "### Changed" not in markdown
        assert "### Fixed" not in markdown

    def test_changelog_with_all_sections(self):
        """Test changelog with all section types."""
        all_sections = {
            "Breaking": ["- breaking change"],
            "Added": ["- new feature"],
            "Changed": ["- change"],
            "Fixed": ["- bug fix"],
            "Removed": ["- removed feature"],
        }

        changelog = ChangelogContent(
            version="v0.3.0",
            date="2026-04-19",
            sections=all_sections,
        )

        markdown = changelog.to_markdown()

        for section_name in all_sections:
            assert f"### {section_name}" in markdown
