"""Tests for the AI-powered changelog agent."""

import tempfile
from pathlib import Path

import pytest

try:
    PYDANTIC_AI_AVAILABLE = True
    from tools.changelog_agent import ChangelogAgent, ChangelogContent, CommitInfo
except ImportError:
    PYDANTIC_AI_AVAILABLE = False
    CommitInfo = None
    ChangelogContent = None
    ChangelogAgent = None

# Skip all tests if pydantic-ai is not available
pytestmark = pytest.mark.skipif(
    not PYDANTIC_AI_AVAILABLE,
    reason="pydantic-ai not installed"
)


class TestCommitInfo:
    """Test CommitInfo model."""

    def test_create_commit_info(self):
        """Test creating CommitInfo."""
        commit = CommitInfo(
            hash="abc123",
            type="feat",
            scope="tutor",
            subject="add adaptive hint policy",
            breaking=False,
        )
        assert commit.type == "feat"
        assert commit.scope == "tutor"
        assert not commit.breaking

    def test_breaking_change(self):
        """Test breaking change detection."""
        commit = CommitInfo(
            hash="abc123",
            type="feat",
            scope="api",
            subject="change session schema",
            breaking=True,
        )
        assert commit.breaking


class TestChangelogContent:
    """Test ChangelogContent model."""

    def test_create_changelog_content(self):
        """Test creating ChangelogContent."""
        changelog = ChangelogContent(
            version="v0.2.0",
            date="2026-04-18",
            sections={
                "Added": ["- (tutor): add adaptive hints"],
                "Fixed": ["- (core): fix critical bug"],
            },
            summary="Major feature release with improvements",
        )
        assert changelog.version == "v0.2.0"
        assert "Added" in changelog.sections
        assert len(changelog.sections["Added"]) == 1

    def test_empty_sections(self):
        """Test changelog with no changes."""
        changelog = ChangelogContent(
            version="v0.2.0",
            date="2026-04-18",
            sections={},
            summary="No changes in this release.",
        )
        assert not changelog.sections


class TestChangelogAgent:
    """Test ChangelogAgent functionality."""

    def test_invalid_repo_raises_error(self):
        """Test that invalid repo path raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="Not a git repository"):
                ChangelogAgent(repo_path=tmpdir)

    def test_agent_initialization(self):
        """Test agent initialization with valid repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Initialize git repo
            import subprocess
            subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
            
            agent = ChangelogAgent(repo_path=str(repo_path))
            assert agent.model is not None
            assert agent.repo_path == repo_path

    def test_format_changelog_entry_structure(self):
        """Test formatting changelog content as markdown."""
        changelog = ChangelogContent(
            version="v0.2.0",
            date="2026-04-18",
            sections={
                "Added": [
                    "(tutor): add adaptive hint policy",
                    "(assessment): new evaluation metrics",
                ],
                "Fixed": ["(core): fix critical bug"],
            },
            summary="Feature release",
        )
        
        agent = ChangelogAgent()
        formatted = agent.format_changelog_entry(changelog)
        
        assert "## [v0.2.0] - 2026-04-18" in formatted
        assert "### Added" in formatted
        assert "### Fixed" in formatted
        assert "(tutor): add adaptive hint policy" in formatted

    def test_format_changelog_entry_section_order(self):
        """Test that sections are ordered correctly."""
        changelog = ChangelogContent(
            version="v0.2.0",
            date="2026-04-18",
            sections={
                "Fixed": ["entry"],
                "Added": ["entry"],
                "Breaking": ["entry"],
                "Removed": ["entry"],
                "Changed": ["entry"],
            },
            summary="Test",
        )
        
        agent = ChangelogAgent()
        formatted = agent.format_changelog_entry(changelog)
        
        # Find positions of sections
        breaking_pos = formatted.find("### Breaking")
        added_pos = formatted.find("### Added")
        changed_pos = formatted.find("### Changed")
        fixed_pos = formatted.find("### Fixed")
        removed_pos = formatted.find("### Removed")
        
        # Verify order: Breaking, Added, Changed, Fixed, Removed
        assert breaking_pos < added_pos < changed_pos < fixed_pos < removed_pos

    def test_get_system_prompt(self):
        """Test system prompt generation."""
        agent = ChangelogAgent()
        prompt = agent._get_system_prompt()
        
        assert "changelog" in prompt.lower()
        assert "Added" in prompt
        assert "Breaking" in prompt


class TestChangelogAgentIntegration:
    """Integration tests with temporary git repository."""

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
            changelog.write_text("# Changelog\n\nAll notable changes.\n")
            
            subprocess.run(["git", "add", "CHANGELOG.md"], cwd=repo_path, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "chore(repo): initial changelog"],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )
            
            yield repo_path

    def test_update_changelog_file(self, temp_git_repo):
        """Test updating CHANGELOG.md file."""
        repo_path = temp_git_repo
        
        agent = ChangelogAgent(repo_path=str(repo_path))
        changelog = ChangelogContent(
            version="v0.1.0",
            date="2026-04-18",
            sections={
                "Added": ["(test): test feature"],
            },
            summary="Initial release",
        )
        
        agent.update_changelog(changelog, "CHANGELOG.md")
        
        changelog_content = (repo_path / "CHANGELOG.md").read_text()
        assert "## [v0.1.0] - 2026-04-18" in changelog_content
        assert "### Added" in changelog_content
        assert "(test): test feature" in changelog_content

    def test_format_commits_for_agent(self, temp_git_repo):
        """Test formatting commits for agent analysis."""
        repo_path = temp_git_repo
        
        commits = [
            CommitInfo(
                hash="abc123",
                type="feat",
                scope="tutor",
                subject="add adaptive hints",
                breaking=False,
            ),
            CommitInfo(
                hash="def456",
                type="fix",
                scope="core",
                subject="fix critical bug",
                breaking=False,
            ),
            CommitInfo(
                hash="ghi789",
                type="feat",
                scope="api",
                subject="change schema",
                breaking=True,
            ),
        ]
        
        agent = ChangelogAgent(repo_path=str(repo_path))
        formatted = agent._format_commits_for_agent(commits, "curriculum,architecture")
        
        assert "feat(tutor)" in formatted
        assert "fix(core)" in formatted
        assert "[BREAKING]" in formatted
        assert "curriculum,architecture" in formatted

    def test_generate_fallback_changelog(self, temp_git_repo):
        """Test fallback changelog generation."""
        repo_path = temp_git_repo
        
        commits = [
            CommitInfo(
                hash="abc123",
                type="feat",
                scope="tutor",
                subject="add adaptive hints",
                breaking=False,
            ),
            CommitInfo(
                hash="def456",
                type="fix",
                scope="core",
                subject="fix critical bug",
                breaking=False,
            ),
        ]
        
        agent = ChangelogAgent(repo_path=str(repo_path))
        changelog = agent._generate_fallback_changelog("v0.2.0", commits, "2026-04-18")
        
        assert changelog.version == "v0.2.0"
        assert "Added" in changelog.sections
        assert "Fixed" in changelog.sections
