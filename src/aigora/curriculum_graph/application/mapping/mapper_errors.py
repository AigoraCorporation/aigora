class GraphMapperError(Exception):
    """Base exception for curriculum graph mapping errors."""


class InvalidGraphPayloadError(GraphMapperError):
    """Raised when the top-level payload is invalid for mapping."""


class InvalidNodePayloadError(GraphMapperError):
    """Raised when a node payload is invalid for mapping."""


class InvalidEdgePayloadError(GraphMapperError):
    """Raised when an edge payload is invalid for mapping."""


class InvalidProfilePayloadError(GraphMapperError):
    """Raised when a profile payload is invalid for mapping."""