"""Integration tests for Neo4jClient.

These tests require a running local Neo4j instance.
Configure via environment variables or a .env file:
    NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

Run only when Neo4j is available:
    NEO4J_INTEGRATION_TESTS=1 pytest -m integration tests/integration/curriculum_graph/infrastructure/neo4j/
"""
from __future__ import annotations

import os

import pytest

from aigora.curriculum_graph.infrastructure.neo4j.neo4j_client import (
    Neo4jClient,
)
from aigora.curriculum_graph.infrastructure.neo4j.errors import (
    Neo4jClientError,
)

_NEO4J_INTEGRATION = bool(os.environ.get("NEO4J_INTEGRATION_TESTS"))


@pytest.mark.integration
@pytest.mark.skipif(
    not _NEO4J_INTEGRATION,
    reason="Set NEO4J_INTEGRATION_TESTS=1 to run Neo4j integration tests",
)
class TestNeo4jClientIntegration:
    """Integration tests against a live local Neo4j instance."""

    @pytest.fixture
    def client(self) -> Neo4jClient:
        client = Neo4jClient(
            uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            username=os.environ.get("NEO4J_USERNAME", "neo4j"),
            password=os.environ.get("NEO4J_PASSWORD", "aigora-local-password"),
            database=os.environ.get("NEO4J_DATABASE", "neo4j"),
        )

        yield client

        client.close()

    def test_simple_connection_and_query(self, client: Neo4jClient) -> None:
        """Client connects to Neo4j and executes a simple query successfully."""
        results = client.run("RETURN 1 AS check")
        assert results == [{"check": 1}]

    def test_parameterized_query(self, client: Neo4jClient) -> None:
        """Client executes a parameterized query and returns correct results."""
        results = client.run("RETURN $value AS result", {"value": "aigora"})
        assert results == [{"result": "aigora"}]

    def test_session_closes_after_context_exit(self, client: Neo4jClient) -> None:
        """Session resources are released after session context manager exits."""
        with client.session() as session:
            result = session.run("RETURN 42 AS n")
            assert result.single()["n"] == 42

    def test_invalid_query_raises_neo4j_client_error(self, client: Neo4jClient) -> None:
        """An invalid Cypher query raises Neo4jClientError."""
        with pytest.raises(Neo4jClientError):
            client.run("THIS IS NOT CYPHER")

    def test_missing_env_variable_raises_key_error(self) -> None:
        """Missing required environment variable raises KeyError."""
        env_backup = os.environ.pop("NEO4J_URI", None)
        try:
            with pytest.raises(KeyError):
                Neo4jClient(uri=None, username="neo4j", password="password")
        finally:
            if env_backup is not None:
                os.environ["NEO4J_URI"] = env_backup