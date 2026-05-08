class GraphSerializerError(Exception):
    """Base exception for curriculum graph serialization errors."""


class UnsupportedSerializationFormatError(GraphSerializerError):
    """Raised when the requested serialization format is not supported."""
