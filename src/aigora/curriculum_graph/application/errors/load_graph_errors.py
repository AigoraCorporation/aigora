class LoadGraphError(Exception):
    """Raised when CurriculumGraph loading fails."""


class InvalidGraphVersionError(LoadGraphError):
    """Raised when the raw graph payload has an invalid version field."""
