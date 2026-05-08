class GraphParserError(Exception):
    """Base exception for curriculum graph parsing errors."""


class UnsupportedGraphFileFormatError(GraphParserError):
    """Raised when the file extension is not supported."""


class GraphFileReadError(GraphParserError):
    """Raised when the graph file cannot be read."""


class GraphFileParseError(GraphParserError):
    """Raised when the graph file content is malformed."""


class GraphStructureError(GraphParserError):
    """Raised when the parsed graph structure is invalid."""