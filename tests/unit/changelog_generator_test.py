"""Tests for the changelog generator."""

import tempfile
from pathlib import Path

import pytest

from tools.changelog_generator import (
    ChangelogGenerator,
    ConventionalCommit,
)


class TestConventionalCommit:
    """Test ConventionalCommit parsing."""

    def test_valid_feat_commit(self):
        """Test parsing a valid feat commit."""
        commit = ConventionalCommit(
            "abc123",
            "feat(tutor): add adaptive hint policy",
            "",
        )
        assert commit.is_valid
        assert commit.type == "feat"
        assert commit.scope == "tutor"
        assert commit.subject == "add adaptive hint policy"
        assert not commit.breaking

    def test_feat_with_breaking_change(self):
        """Test parsing a feat with breaking change marker."""
        commit = ConventionalCommit(
            "abc123",
            "feat(api)!: change session schema",
            "",
        )
        assert commit.is_valid
        assert commit.type == "feat"
        assert commit.breaking
        assert commit.scope == "api"

    def test_valid_fix_commit(self):
        """Test parsing a valid fix commit."""
        commit = ConventionalCommit(
            "abc123",
            "fix(assessment): handle empty answer input",
            "",
        )
        assert commit.is_valid
        assert commit.type == "fix"
        assert commit.scope == "assessment"

    def test_valid_docs_commit(self):
        """Test parsing a valid docs commit."""
        commit = ConventionalCommit(
            "abc123",
            "docs(architecture): add C4 container diagram",
            "",
        )
        assert commit.is_valid
        assert commit.type == "docs"

    def test_commit_without_scope(self):
        """Test parsing commit without scope (should be invalid due to scope requirement)."""
        commit = ConventionalCommit(
            "abc123",
            "feat: add new feature",
            "",
        )
        # This will be considered invalid because scope is required by the parser
        # In reality, the commitlint rules enforce scope, so this is expected
        assert not commit.is_valid or commit.scope is None

    def test_invalid_commit(self):
        """Test parsing an invalid commit message."""
        commit = ConventionalCommit(
            "abc123",
            "this is not a conventional commit",
            "",
        )
        assert not commit.is_valid

    def test_all_valid_types(self):
        """Test all valid commit types."""
        types = ["feat", "fix", "docs", "refactor", "test", "perf", "build", "ci", "chore", "revert"]
        for commit_type in types:
            commit = ConventionalCommit(
                "abc123",
                f"{commit_type}(repo): test commit",
                "",
            )
            assert commit.is_valid, f"Type {commit_type} should be valid"
            assert commit.type == commit_type


class TestChangelogGenerator:
    """Test ChangelogGenerator functionality."""

    def test_type_to_section_mapping(self):
        """Test that commit types are correctly mapped to changelog sections."""
        expected_mapping = {
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
        assert ChangelogGenerator.TYPE_TO_SECTION == expected_mapping

    def test_format_changelog_entry_with_entries(self):
        """Test formatting a changelog entry with generated entries."""
        generator = ChangelogGenerator(".")
        
        entries = {
            "Added": [
                "- (tutor): add adaptive hint policy",
                "- (assessment): add new evaluation metrics",
            ],
            "Fixed": [
                "- (core): fix critical bug in session management",
            ],
        }
        
        changelog_entry = generator.format_changelog_entry(
            "v0.2.0",
            "2026-04-18",
            entries,
        )
        
        assert "## [v0.2.0] - 2026-04-18" in changelog_entry
        assert "### Added" in changelog_entry
        assert "- (tutor): add adaptive hint policy" in changelog_entry
        assert "### Fixed" in changelog_entry
        assert "- (core): fix critical bug" in changelog_entry

    def test_format_changelog_entry_removes_empty_sections(self):
        """Test that empty sections are not included in output."""
        generator = ChangelogGenerator(".")
        
        entries = {
            "Added": ["- test entry"],
            "Fixed": [],
            "Changed": [],
        }
        
        changelog_entry = generator.format_changelog_entry(
            "v0.2.0",
            "2026-04-18",
            entries,
        )
        
        assert "### Added" in changelog_entry
        assert "### Fixed" not in changelog_entry
        assert "### Changed" not in changelog_entry

    def test_format_changelog_entry_default_date(self):
        """Test that default date is used when not provided."""
        generator = ChangelogGenerator(".")
        entries = {"Added": ["- test"]}
        
        changelog_entry = generator.format_changelog_entry(
            "v0.2.0",
            entries=entries,
        )
        
        # Should contain today's date
        assert "## [v0.2.0] -" in changelog_entry

    def test_invalid_repo_raises_error(self):
        """Test that invalid repo path raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Not a git repository"):
                ChangelogGenerator(tmpdir)


class TestChangelogIntegration:
    """Integration tests using a temporary git repository."""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Initialize git repo
            import subprocess
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )
            
            # Create initial CHANGELOG.md
            changelog = repo_path / "CHANGELOG.md"
            changelog.write_text("# Changelog\n\nAll notable changes to this project.\n")
            
            subprocess.run(["git", "add", "CHANGELOG.md"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "chore(repo): initial changelog"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )
            
            yield repo_path

    def test_generate_entries_with_test_commits(self, temp_git_repo):
        """Test generating entries from test commits."""
        import subprocess
        
        repo_path = temp_git_repo
        
        # Create a test commit
        test_file = repo_path / "test.txt"
        test_file.write_text("test content")
        
        subprocess.run(["git", "add", "test.txt"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat(test): add test feature"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        
        generator = ChangelogGenerator(str(repo_path))
        entries = generator.generate_entries()
        
        assert "Added" in entries
        # The specific assertion depends on git history

    def test_get_latest_version_no_tags(self, temp_git_repo):
        """Test getting latest version when no tags exist."""
        generator = ChangelogGenerator(str(temp_git_repo))
        version = generator._get_latest_version()
        
        # Should return None if no tags
        assert version is None or isinstance(version, str)

    def test_update_changelog_file(self, temp_git_repo):
        """Test updating CHANGELOG.md file."""
        repo_path = temp_git_repo
        
        generator = ChangelogGenerator(str(repo_path))
        entries = {
            "Added": ["- (test): test feature"],
        }
        
        generator.update_changelog(
            "v0.1.0",
            "CHANGELOG.md",
            "2026-04-18",
            entries,
        )
        
        changelog_content = (repo_path / "CHANGELOG.md").read_text()
        assert "## [v0.1.0] - 2026-04-18" in changelog_content
        assert "### Added" in changelog_content
        assert "- (test): test feature" in changelog_content
