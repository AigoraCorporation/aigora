class GraphValidationError(Exception):
    """Base exception for curriculum graph validation errors."""


class InvalidNodeIdFormatError(GraphValidationError):
    """Raised when a node id does not conform to the authoring convention."""


class InvalidProfileIdFormatError(GraphValidationError):
    """Raised when a profile id does not conform to the authoring convention."""


class InvalidEdgeReferenceError(GraphValidationError):
    """Raised when an edge references a node that does not exist."""


class CyclicDependencyError(GraphValidationError):
    """Raised when a prerequisite cycle is detected in the graph."""


class InvalidNodeMasteryDefinitionError(GraphValidationError):
    """Raised when a node mastery definition is inconsistent."""


class InvalidProfileReferenceError(GraphValidationError):
    """Raised when a profile references a node that does not exist."""


class InvalidProfileMasteryTargetError(GraphValidationError):
    """Raised when a profile mastery target is invalid or unsupported."""


class InvalidProfileProgressionPathError(GraphValidationError):
    """Raised when a profile progression path is inconsistent with prerequisite order."""


class InvalidProfileWeightError(GraphValidationError):
    """Raised when a profile weight is zero or negative."""