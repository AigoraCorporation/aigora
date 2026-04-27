class GraphVersioningError(Exception):
    """Base exception for curriculum graph versioning errors."""


class MissingVersionError(GraphVersioningError):
    """Raised when a required version field is absent."""


class InvalidVersionFormatError(GraphVersioningError):
    """Raised when a version string does not conform to the expected format."""
