class CurriculumGraphSerializerError(Exception):
    """Base exception for curriculum graph serialization errors."""


class UnsupportedSerializationFormatError(CurriculumGraphSerializerError):
    """Raised when the requested serialization format is not supported."""
