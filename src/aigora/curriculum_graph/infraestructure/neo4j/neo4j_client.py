from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from neo4j import GraphDatabase, Session


class Neo4jClientError(Exception):
    """Raised when a Neo4j infrastructure operation fails."""


class Neo4jClient:
    """Low-level Neo4j connection and query execution client.

    Reads configuration from environment variables. Does not contain
    domain rules, application orchestration, or repository-specific
    persistence logic.

    Environment variables:
        NEO4J_URI       — Bolt URI (e.g. bolt://localhost:7687)
        NEO4J_USERNAME  — Database username
        NEO4J_PASSWORD  — Database password
        NEO4J_DATABASE  — Target database (default: neo4j)
    """

    def __init__(
        self,
        uri: str | None = None,
        username: str | None = None,
        password: str | None = None,
        database: str | None = None,
    ) -> None:
        self._uri = uri or os.environ["NEO4J_URI"]
        self._username = username or os.environ["NEO4J_USERNAME"]
        self._password = password or os.environ["NEO4J_PASSWORD"]
        self._database = database or os.environ.get("NEO4J_DATABASE", "neo4j")
        self._driver = GraphDatabase.driver(
            self._uri, auth=(self._username, self._password)
        )

    def close(self) -> None:
        """Close the underlying driver and release all resources."""
        self._driver.close()

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Yield a managed Neo4j session. Closes on exit."""
        session = self._driver.session(database=self._database)
        try:
            yield session
        finally:
            session.close()

    def run(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Execute a parameterized Cypher query and return results as a list of dicts.

        Args:
            query: Cypher query string.
            parameters: Optional dict of query parameters.

        Returns:
            List of result records as plain dicts.

        Raises:
            Neo4jClientError: If query execution fails.
        """
        params = parameters or {}
        try:
            with self.session() as s:
                result = s.run(query, params)
                return [record.data() for record in result]
        except Exception as exc:
            raise Neo4jClientError(
                f"Query execution failed: {exc}"
            ) from exc

    def __enter__(self) -> Neo4jClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
