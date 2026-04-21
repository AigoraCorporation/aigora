class GraphSchemaError(Exception):
    """Base exception for curriculum graph schema validation errors."""


class SchemaValidationError(GraphSchemaError):
    """Raised when a parsed graph payload fails schema validation."""
