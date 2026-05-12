"""Integration tests for Neo4jCurriculumGraphRepository against a live Neo4j instance.

Requires a running local Neo4j instance.
Configure via environment variables:
    NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

Run only when Neo4j is available:
    NEO4J_INTEGRATION_TESTS=1 pytest -m integration tests/integration/curriculum_graph/infrastructure/neo4j/
"""
from __future__ import annotations

import os

import pytest

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.entities.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.entities.edge import Edge
from aigora.curriculum_graph.domain.enums.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.value_objects.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.entities.node import Node
from aigora.curriculum_graph.infrastructure.neo4j.neo4j_client import Neo4jClient
from aigora.curriculum_graph.infrastructure.neo4j.neo4j_curriculum_graph_repository import (
    Neo4jCurriculumGraphRepository,
)

_NEO4J_INTEGRATION = bool(os.environ.get("NEO4J_INTEGRATION_TESTS"))


def _make_graph() -> CurriculumGraph:
    graph = CurriculumGraph()
    n1 = Node(
        id="integ-n1",
        name="Integration Node 1",
        domain="math",
        description="Integration test node 1",
        mastery_criteria=MasteryScale(
            criteria_by_level={
                MasteryLevel.GUIDED: MasteryCriterion(
                    level=MasteryLevel.GUIDED, description="Guided"
                )
            }
        ),
    )
    n2 = Node(
        id="integ-n2",
        name="Integration Node 2",
        domain="math",
        description="Integration test node 2",
        mastery_criteria=MasteryScale(
            criteria_by_level={
                MasteryLevel.INDEPENDENT: MasteryCriterion(
                    level=MasteryLevel.INDEPENDENT, description="Independent"
                )
            }
        ),
    )
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_edge(Edge(type=EdgeType.HARD_PREREQUISITE, source="integ-n1", target="integ-n2"))
    graph.add_profile(CurriculumProfile(
        id="integ-p1",
        name="Integration Profile 1",
        required_nodes={"integ-n1", "integ-n2"},
    ))
    return graph


@pytest.mark.integration
@pytest.mark.skipif(
    not _NEO4J_INTEGRATION,
    reason="Set NEO4J_INTEGRATION_TESTS=1 to run Neo4j integration tests",
)
class TestNeo4jCurriculumGraphRepositoryIntegration:
    @pytest.fixture
    def client(self) -> Neo4jClient:
        return Neo4jClient(
            uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            username=os.environ.get("NEO4J_USERNAME", "neo4j"),
            password=os.environ.get("NEO4J_PASSWORD", "aigora-local-password"),
            database=os.environ.get("NEO4J_DATABASE", "neo4j"),
        )

    @pytest.fixture
    def repo(self, client: Neo4jClient) -> Neo4jCurriculumGraphRepository:
        return Neo4jCurriculumGraphRepository(client=client)

    @pytest.fixture(autouse=True)
    def cleanup(self, client: Neo4jClient):
        yield
        with client:
            client.run("MATCH (n:Concept) WHERE n.id STARTS WITH 'integ-' DETACH DELETE n")
            client.run("MATCH (p:CurriculumProfile) WHERE p.id STARTS WITH 'integ-' DELETE p")

    def test_persist_and_validate(self, repo: Neo4jCurriculumGraphRepository, client: Neo4jClient) -> None:
        graph = _make_graph()
        with client:
            repo.apply_schema()
            repo.persist(graph)
            repo.validate(graph)

    def test_persist_is_idempotent(self, repo: Neo4jCurriculumGraphRepository, client: Neo4jClient) -> None:
        graph = _make_graph()
        with client:
            repo.persist(graph)
            repo.persist(graph)  # second run must not duplicate
            repo.validate(graph)
