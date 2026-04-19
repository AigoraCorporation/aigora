"""Data models for changelog generation."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Commit(BaseModel):
    """Represents a parsed conventional commit."""

    hash: str = Field(..., description="Git commit hash")
    type: str = Field(..., description="Commit type (feat, fix, etc.)")
    scope: Optional[str] = Field(None, description="Commit scope (component name)")
    subject: str = Field(..., description="Commit subject line")
    body: str = Field(default="", description="Commit body/message")
    breaking: bool = Field(default=False, description="Whether this is a breaking change")

    def to_conventional_format(self) -> str:
        """Format as conventional commit string."""
        prefix = self.type
        if self.scope:
            prefix += f"({self.scope})"
        if self.breaking:
            prefix += "!"
        return f"{prefix}: {self.subject}"


class ChangelogSection(BaseModel):
    """Represents a changelog section with entries."""

    section: str = Field(..., description="Section name: Added, Changed, Fixed, Removed, Breaking")
    entries: List[str] = Field(..., description="List of changelog entries")

    def is_empty(self) -> bool:
        """Check if section has no entries."""
        return not self.entries

    def to_markdown(self) -> str:
        """Convert to markdown format."""
        if self.is_empty():
            return ""
        lines = [f"### {self.section}"]
        lines.extend(self.entries)
        lines.append("")
        return "\n".join(lines)


class ChangelogContent(BaseModel):
    """Complete changelog content for a version."""

    version: str = Field(..., description="Version identifier (e.g., v0.2.0)")
    date: str = Field(..., description="Release date (YYYY-MM-DD)")
    sections: Dict[str, List[str]] = Field(default_factory=dict, description="Changelog sections with entries")
    summary: str = Field(default="", description="Brief summary of major changes")

    def to_markdown(self) -> str:
        """Convert to markdown format."""
        lines = [f"## [{self.version}] - {self.date}\n"]

        # Order sections properly
        section_order = ["Breaking", "Added", "Changed", "Fixed", "Removed"]
        for section in section_order:
            if section in self.sections and self.sections[section]:
                lines.append(f"### {section}")
                for entry in self.sections[section]:
                    lines.append(f"- {entry}")
                lines.append("")

        return "\n".join(lines)
