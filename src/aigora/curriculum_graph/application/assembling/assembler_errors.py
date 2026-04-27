class GraphAssemblerError(Exception):
    """Base exception for curriculum graph assembly errors."""


class DuplicateNodeError(GraphAssemblerError):
    """Raised when a node with a duplicate id is added during assembly."""


class DuplicateProfileError(GraphAssemblerError):
    """Raised when a profile with a duplicate id is added during assembly."""


class UnresolvedNodeReferenceError(GraphAssemblerError):
    """Raised when an edge or profile references a node id that is not present in the graph."""
