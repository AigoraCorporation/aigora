from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, TYPE_CHECKING

from aigora.shared.config.settings import Neo4jSettings
from aigora.curriculum_graph.infrastructure.neo4j.errors import Neo4jClientError

if TYPE_CHECKING:
    from neo4j import Session
else:
    Session = Any

try:
    from neo4j import GraphDatabase
except ModuleNotFoundError:  # pragma: no cover - exercised only when dependency is absent
    GraphDatabase = None



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
        settings = None
        if uri is None or username is None or password is None:
            settings = Neo4jSettings.from_env()

        self._uri = uri or settings.uri
        self._username = username or settings.username
        self._password = password or settings.password
        self._database = database or settings.database
        if GraphDatabase is None:
            raise Neo4jClientError(
                "The 'neo4j' package is required to create Neo4jClient. "
                "Install project dependencies before using the Neo4j infrastructure adapter."
            )

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
