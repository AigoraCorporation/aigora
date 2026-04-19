"""Tests for the agent module."""

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import ChangelogAgent, CommitInfo
from models import ChangelogContent


class TestCommitInfo:
    """Tests for CommitInfo model."""

    def test_commit_info_creation(self):
        """Test creating CommitInfo."""
        info = CommitInfo(
            hash="abc123",
            type="feat",
            scope="test",
            subject="test feature",
            breaking=False,
        )

        assert info.hash == "abc123"
        assert info.type == "feat"
        assert info.scope == "test"

    def test_commit_info_optional_scope(self):
        """Test CommitInfo with optional scope."""
        info = CommitInfo(
            hash="abc123",
            type="fix",
            subject="fix bug",
            breaking=False,
        )

        assert info.scope is None


class TestChangelogAgent:
    """Tests for ChangelogAgent."""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize git repo
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

            # Create CHANGELOG.md
            changelog = repo_path / "CHANGELOG.md"
            changelog.write_text("# Changelog\n\nAll notable changes.\n")

            yield repo_path

    def test_agent_initialization_invalid_repo(self):
        """Test that invalid repo path raises error."""
        with pytest.raises(ValueError, match="Not a git repository"):
            ChangelogAgent(repo_path="/nonexistent/path")

    @patch("agent.Agent")
    def test_agent_initialization_valid_repo(self, mock_agent_class, temp_git_repo):
        """Test successful agent initialization."""
        # Mock the Agent to avoid requiring API keys
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))

        assert agent.model == "claude-3-5-sonnet-20241022"
        assert agent.repo_path == temp_git_repo

    @patch("agent.Agent")
    def test_agent_custom_model(self, mock_agent_class, temp_git_repo):
        """Test agent with custom model."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(model="gpt-4o-mini", repo_path=str(temp_git_repo))

        assert agent.model == "gpt-4o-mini"

    @patch("agent.Agent")
    def test_get_system_prompt(self, mock_agent_class, temp_git_repo):
        """Test that system prompt is generated."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))
        prompt = agent._get_system_prompt()

        assert "changelog" in prompt.lower()
        assert "Added" in prompt
        assert "Changed" in prompt
        assert "Fixed" in prompt

    @patch("agent.Agent")
    def test_format_commits_for_agent(self, mock_agent_class, temp_git_repo):
        """Test formatting commits for agent."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))

        commits = [
            CommitInfo(
                hash="abc123",
                type="feat",
                scope="test",
                subject="add feature",
                breaking=False,
            ),
            CommitInfo(
                hash="def456",
                type="fix",
                scope="bug",
                subject="fix issue",
                breaking=False,
            ),
        ]

        formatted = agent._format_commits_for_agent(commits)

        assert "feat(test)" in formatted
        assert "add feature" in formatted
        assert "fix(bug)" in formatted
        assert "fix issue" in formatted

    @patch("agent.Agent")
    def test_format_commits_with_breaking(self, mock_agent_class, temp_git_repo):
        """Test formatting commits with breaking changes."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))

        commits = [
            CommitInfo(
                hash="abc123",
                type="feat",
                scope="api",
                subject="change schema",
                breaking=True,
            ),
        ]

        formatted = agent._format_commits_for_agent(commits)

        assert "[BREAKING]" in formatted

    @patch("agent.Agent")
    def test_format_commits_with_docs_scope(self, mock_agent_class, temp_git_repo):
        """Test formatting with documentation scope."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))

        commits = [
            CommitInfo(
                hash="abc123",
                type="feat",
                scope="test",
                subject="test",
                breaking=False,
            ),
        ]

        formatted = agent._format_commits_for_agent(commits, docs_scope="curriculum,architecture")

        assert "Documentation scope:" in formatted
        assert "curriculum,architecture" in formatted

    @patch("agent.Agent")
    def test_generate_fallback_changelog(self, mock_agent_class, temp_git_repo):
        """Test fallback changelog generation."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))

        commits = [
            CommitInfo(
                hash="abc123",
                type="feat",
                scope="test",
                subject="add feature",
                breaking=False,
            ),
            CommitInfo(
                hash="def456",
                type="fix",
                scope="bug",
                subject="fix bug",
                breaking=False,
            ),
            CommitInfo(
                hash="ghi789",
                type="refactor",
                scope="core",
                subject="refactor code",
                breaking=False,
            ),
        ]

        changelog = agent._generate_fallback_changelog("v0.2.0", commits)

        assert changelog.version == "v0.2.0"
        assert "Added" in changelog.sections
        assert "Fixed" in changelog.sections
        assert "Changed" in changelog.sections

    @patch("agent.Agent")
    def test_generate_fallback_changelog_with_breaking(self, mock_agent_class, temp_git_repo):
        """Test fallback with breaking changes."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))

        commits = [
            CommitInfo(
                hash="abc123",
                type="feat",
                scope="api",
                subject="change schema",
                breaking=True,
            ),
        ]

        changelog = agent._generate_fallback_changelog("v0.2.0", commits)

        assert "Breaking" in changelog.sections

    @patch("agent.Agent")
    def test_generate_fallback_changelog_deduplicates(self, mock_agent_class, temp_git_repo):
        """Test that fallback deduplicates identical commits."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))

        # Same commit appearing twice (e.g., present in two branches merged together)
        commits = [
            CommitInfo(hash="abc123", type="feat", scope="api", subject="add endpoint", breaking=False),
            CommitInfo(hash="def456", type="feat", scope="api", subject="add endpoint", breaking=False),
            CommitInfo(hash="ghi789", type="fix", scope="bug", subject="fix crash", breaking=False),
        ]

        changelog = agent._generate_fallback_changelog("v0.2.0", commits)

        assert len(changelog.sections["Added"]) == 1
        assert len(changelog.sections["Fixed"]) == 1

    @patch("agent.Agent")
    def test_format_changelog_entry(self, mock_agent_class, temp_git_repo):
        """Test changelog formatting."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))

        changelog = ChangelogContent(
            version="v0.2.0",
            date="2026-04-18",
            sections={
                "Added": ["- (test): add feature"],
                "Fixed": ["- (bug): fix issue"],
            },
        )

        formatted = agent.format_changelog_entry(changelog)

        assert "## [v0.2.0] - 2026-04-18" in formatted
        assert "### Added" in formatted
        assert "### Fixed" in formatted

    @patch("agent.Agent")
    def test_update_changelog_file_not_found(self, mock_agent_class, temp_git_repo):
        """Test error when changelog file doesn't exist."""
        mock_agent_class.return_value = MagicMock()

        repo_without_changelog = Path(tempfile.mkdtemp())
        try:
            subprocess.run(["git", "init"], cwd=repo_without_changelog, check=True, capture_output=True)

            agent = ChangelogAgent(repo_path=str(repo_without_changelog))

            changelog = ChangelogContent(
                version="v0.2.0",
                date="2026-04-18",
                sections={},
            )

            with pytest.raises(FileNotFoundError):
                agent.update_changelog(changelog)
        finally:
            import shutil
            shutil.rmtree(repo_without_changelog)

    @patch("agent.Agent")
    def test_update_changelog_inserts_new_entry(self, mock_agent_class, temp_git_repo):
        """Test that update_changelog inserts new entry."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))

        changelog = ChangelogContent(
            version="v0.2.0",
            date="2026-04-18",
            sections={
                "Added": ["- (feature): new feature"],
            },
        )

        agent.update_changelog(changelog, "CHANGELOG.md")

        # Read and verify
        content = (temp_git_repo / "CHANGELOG.md").read_text()

        assert "## [v0.2.0] - 2026-04-18" in content
        assert "### Added" in content
        assert "- (feature): new feature" in content

    @patch("agent.Agent")
    def test_no_commits_in_range(self, mock_agent_class, temp_git_repo):
        """Test handling of no commits."""
        mock_agent_class.return_value = MagicMock()

        agent = ChangelogAgent(repo_path=str(temp_git_repo))

        # Create a conventional commit
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("content")
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat(test): test feature"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        # Tag it
        subprocess.run(
            ["git", "tag", "v0.1.0"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        # Get commits since tag (should be empty)
        agent2 = ChangelogAgent(repo_path=str(temp_git_repo))
        commits = agent2._get_commits_since_last_version()

        assert commits == []


class TestChangelogAgentIntegration:
    """Integration tests for ChangelogAgent."""

    @pytest.fixture
    def temp_git_repo_with_commits(self):
        """Create a git repo with sample commits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)

            # Initialize
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

            # Create CHANGELOG
            changelog = repo_path / "CHANGELOG.md"
            changelog.write_text("# Changelog\n\n## [v0.1.0] - 2026-04-17\n\n### Added\n- initial\n")

            # Create commits
            test_file = repo_path / "test.txt"

            test_file.write_text("v1")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "feat(feature): add new feature"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

            test_file.write_text("v2")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "fix(bug): fix critical bug"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

            # Tag
            subprocess.run(
                ["git", "tag", "v0.1.0"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

            test_file.write_text("v3")
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "feat(new): another feature"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )

            yield repo_path

    def test_full_changelog_generation_flow(self, temp_git_repo_with_commits):
        """Test the full changelog generation flow."""
        with patch("agent.Agent"):
            agent = ChangelogAgent(repo_path=str(temp_git_repo_with_commits))

            # Get commits since last tag
            commits = agent._get_commits_since_last_version()

            assert len(commits) == 1
            assert commits[0].type == "feat"

            # Generate fallback changelog
            changelog = agent._generate_fallback_changelog("v0.2.0", commits)

            assert changelog.version == "v0.2.0"
            assert "Added" in changelog.sections

            # Format and update
            formatted = agent.format_changelog_entry(changelog)
            assert "v0.2.0" in formatted

            # Update file
            agent.update_changelog(changelog)

            # Verify
            content = (temp_git_repo_with_commits / "CHANGELOG.md").read_text()
            assert "## [v0.2.0]" in content
