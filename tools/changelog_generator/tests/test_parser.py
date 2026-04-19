"""Tests for the parser module."""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Commit
from parser import ConventionalCommitParser, GitCommitReader


class TestConventionalCommitParser:
    """Tests for ConventionalCommitParser."""

    def test_parse_feat_commit(self):
        """Test parsing a feature commit."""
        message = "feat(tutor): add adaptive hint policy"
        commit = ConventionalCommitParser.parse(message, "abc123")

        assert commit is not None
        assert commit.hash == "abc123"
        assert commit.type == "feat"
        assert commit.scope == "tutor"
        assert commit.subject == "add adaptive hint policy"
        assert not commit.breaking

    def test_parse_fix_commit(self):
        """Test parsing a fix commit."""
        message = "fix(assessment): handle empty answer input"
        commit = ConventionalCommitParser.parse(message, "def456")

        assert commit is not None
        assert commit.type == "fix"
        assert commit.scope == "assessment"

    def test_parse_breaking_change(self):
        """Test parsing a breaking change commit."""
        message = "feat(api)!: change session schema"
        commit = ConventionalCommitParser.parse(message, "ghi789")

        assert commit is not None
        assert commit.breaking
        assert commit.type == "feat"
        assert commit.scope == "api"

    def test_parse_commit_without_scope(self):
        """Test parsing commit without scope."""
        message = "docs: update README"
        commit = ConventionalCommitParser.parse(message, "jkl012")

        assert commit is not None
        assert commit.type == "docs"
        assert commit.scope is None  # Scope is optional
        assert commit.subject == "update README"

    def test_parse_commit_with_body(self):
        """Test parsing commit with body."""
        message = """feat(core): add new feature

This is a detailed description
with multiple lines."""
        commit = ConventionalCommitParser.parse(message, "mno345")

        assert commit is not None
        assert "This is a detailed description" in commit.body

    def test_parse_all_valid_types(self):
        """Test all valid commit types."""
        types = ["feat", "fix", "docs", "refactor", "test", "perf", "build", "ci", "chore", "revert"]

        for commit_type in types:
            message = f"{commit_type}(test): test message"
            commit = ConventionalCommitParser.parse(message, "hash")

            assert commit is not None
            assert commit.type == commit_type

    def test_parse_invalid_format(self):
        """Test parsing invalid commit format."""
        message = "this is not a conventional commit"
        commit = ConventionalCommitParser.parse(message, "abc123")

        assert commit is None

    def test_parse_wrong_type(self):
        """Test parsing with invalid type."""
        message = "invalid(scope): some message"
        commit = ConventionalCommitParser.parse(message, "abc123")

        assert commit is None

    def test_to_conventional_format(self):
        """Test converting Commit back to conventional format."""
        commit = Commit(
            hash="abc123",
            type="feat",
            scope="test",
            subject="add feature",
            breaking=False,
        )

        assert commit.to_conventional_format() == "feat(test): add feature"

    def test_to_conventional_format_breaking(self):
        """Test conventional format with breaking change."""
        commit = Commit(
            hash="abc123",
            type="feat",
            scope="api",
            subject="change schema",
            breaking=True,
        )

        assert commit.to_conventional_format() == "feat(api)!: change schema"


class TestGitCommitReader:
    """Tests for GitCommitReader with temporary repository."""

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

            yield repo_path

    def test_invalid_repo_path(self):
        """Test that invalid repo path raises error."""
        with pytest.raises(RuntimeError):
            reader = GitCommitReader("/nonexistent/path")
            reader.get_commits("HEAD")

    def test_get_commits_empty_repo(self, temp_git_repo):
        """Test getting commits from empty repo."""
        reader = GitCommitReader(str(temp_git_repo))
        # Empty repo has no HEAD, so this should raise an exception
        with pytest.raises(RuntimeError):
            reader.get_commits("HEAD")

    def test_get_commits_with_conventional_commit(self, temp_git_repo):
        """Test reading conventional commits from repo."""
        # Create initial commit
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("initial")
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "chore(repo): initial commit"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        # Create feature commit
        test_file.write_text("feature added")
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat(test): add new feature"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        reader = GitCommitReader(str(temp_git_repo))
        commits = reader.get_commits("HEAD~1..HEAD")

        assert len(commits) == 1
        assert commits[0].type == "feat"
        assert commits[0].scope == "test"
        assert commits[0].subject == "add new feature"

    def test_get_commits_skip_non_conventional(self, temp_git_repo):
        """Test that non-conventional commits are skipped."""
        # Create non-conventional commit
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("content")
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "some random commit message"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        reader = GitCommitReader(str(temp_git_repo))
        commits = reader.get_commits("HEAD")

        # Should not include the non-conventional commit
        assert len(commits) == 0

    def test_get_last_tag_no_tags(self, temp_git_repo):
        """Test getting last tag when none exist."""
        reader = GitCommitReader(str(temp_git_repo))
        tag = reader.get_last_tag()

        assert tag is None

    def test_get_last_tag_with_tags(self, temp_git_repo):
        """Test getting last tag with tags."""
        # Create commit and tag
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("content")
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "chore(repo): initial"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "tag", "v0.1.0"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        reader = GitCommitReader(str(temp_git_repo))
        tag = reader.get_last_tag()

        assert tag == "v0.1.0"

    def test_get_commits_since_last_tag(self, temp_git_repo):
        """Test getting commits since last tag."""
        # Create and tag initial commit
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("initial")
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "chore(repo): initial"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "tag", "v0.1.0"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        # Create new commits after tag
        test_file.write_text("feature 1")
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat(feature): add feature 1"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        test_file.write_text("feature 2")
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "fix(bug): fix bug"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        reader = GitCommitReader(str(temp_git_repo))
        commits = reader.get_commits_since_last_tag()

        assert len(commits) == 2
        # Git returns commits in reverse chronological order (newest first)
        assert commits[0].type == "fix"
        assert commits[1].type == "feat"

    def test_get_commits_with_breaking_change(self, temp_git_repo):
        """Test reading breaking change from commit."""
        test_file = temp_git_repo / "test.txt"
        test_file.write_text("content")
        subprocess.run(["git", "add", "test.txt"], cwd=temp_git_repo, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat(api)!: change API schema"],
            cwd=temp_git_repo,
            check=True,
            capture_output=True,
        )

        reader = GitCommitReader(str(temp_git_repo))
        commits = reader.get_commits("HEAD")

        assert len(commits) == 1
        assert commits[0].breaking
