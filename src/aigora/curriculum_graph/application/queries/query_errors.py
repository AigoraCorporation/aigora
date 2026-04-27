class GraphQueryError(Exception):
    """Base exception for curriculum graph query errors."""


class NodeNotFoundError(GraphQueryError):
    """Raised when a requested node id does not exist in the graph."""


class PathNotFoundError(GraphQueryError):
    """Raised when no path exists between two nodes."""