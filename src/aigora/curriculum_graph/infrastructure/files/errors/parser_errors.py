class CurriculumGraphFileParserError(Exception):
    """Base exception for curriculum graph file parsing errors."""


class UnsupportedGraphFileFormatError(CurriculumGraphFileParserError):
    """Raised when the file extension is not supported."""


class GraphFileReadError(CurriculumGraphFileParserError):
    """Raised when the graph file cannot be read."""


class GraphFileParseError(CurriculumGraphFileParserError):
    """Raised when the graph file content is malformed."""


class GraphStructureError(CurriculumGraphFileParserError):
    """Raised when the parsed graph structure is invalid."""
