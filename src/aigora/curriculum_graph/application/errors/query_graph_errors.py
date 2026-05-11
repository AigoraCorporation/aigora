class QueryGraphError(Exception):
    """Base exception for curriculum graph query errors."""


class NodeNotFoundError(QueryGraphError):
    """Raised when a requested node id does not exist in the graph."""


class PathNotFoundError(QueryGraphError):
    """Raised when no path exists between two nodes."""