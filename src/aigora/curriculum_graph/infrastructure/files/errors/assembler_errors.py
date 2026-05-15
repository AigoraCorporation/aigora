class CurriculumGraphAssemblerError(Exception):
    """Base exception for curriculum graph assembly errors."""


class DuplicateNodeError(CurriculumGraphAssemblerError):
    """Raised when a node with a duplicate id is added during assembly."""


class DuplicateProfileError(CurriculumGraphAssemblerError):
    """Raised when a profile with a duplicate id is added during assembly."""


class UnresolvedNodeReferenceError(CurriculumGraphAssemblerError):
    """Raised when an edge or profile references a node id that is not present in the graph."""
