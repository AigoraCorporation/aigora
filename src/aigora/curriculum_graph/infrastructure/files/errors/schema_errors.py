class GraphSchemaValidationError(Exception):
    """Base exception for curriculum graph schema validation errors."""


class MissingRequiredFieldError(GraphSchemaValidationError):
    """Raised when a parsed graph payload misses a required schema field."""


class SchemaValidationError(GraphSchemaValidationError):
    """Raised when a parsed graph payload fails schema validation."""
