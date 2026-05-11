from __future__ import annotations


class Neo4jClientError(Exception):
    """Raised when a Neo4j infrastructure operation fails."""


class GraphPersistenceValidationError(Exception):
    """Raised when post-persistence validation detects a mismatch."""
