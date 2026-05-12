class CurriculumGraphMapperError(Exception):
    """Base exception for curriculum graph mapping errors."""


class InvalidGraphPayloadError(CurriculumGraphMapperError):
    """Raised when the top-level payload is invalid for mapping."""


class InvalidNodePayloadError(CurriculumGraphMapperError):
    """Raised when a node payload is invalid for mapping."""


class InvalidEdgePayloadError(CurriculumGraphMapperError):
    """Raised when an edge payload is invalid for mapping."""


class InvalidProfilePayloadError(CurriculumGraphMapperError):
    """Raised when a profile payload is invalid for mapping."""