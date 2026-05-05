"""Integration tests for Neo4jGraphRepository against a live Neo4j instance.

Requires a running local Neo4j instance.
Configure via environment variables:
    NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

Run only when Neo4j is available:
    pytest -m integration tests/integration/curriculum_graph/infrastructure/neo4j/
"""
from __future__ import annotations

from collections.abc import Generator
import os

import pytest

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.node import Node
from aigora.curriculum_graph.infrastructure.neo4j.neo4j_client import Neo4jClient
from aigora.curriculum_graph.infrastructure.neo4j.neo4j_graph_repository import (
    Neo4jGraphRepository,
)


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
                    level=MasteryLevel.GUIDED,
                    description="Guided",
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
                    level=MasteryLevel.INDEPENDENT,
                    description="Independent",
                )
            }
        ),
    )

    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_edge(
        Edge(
            type=EdgeType.HARD_PREREQUISITE,
            source="integ-n1",
            target="integ-n2",
        )
    )
    graph.add_profile(
        CurriculumProfile(
            id="integ-p1",
            name="Integration Profile 1",
            required_nodes={"integ-n1", "integ-n2"},
        )
    )

    return graph


@pytest.mark.integration
class TestNeo4jGraphRepositoryIntegration:
    @pytest.fixture
    def client(self) -> Generator[Neo4jClient, None, None]:
        client = Neo4jClient(
            uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            username=os.environ.get("NEO4J_USERNAME", "neo4j"),
            password=os.environ.get("NEO4J_PASSWORD", "aigora-local-password"),
            database=os.environ.get("NEO4J_DATABASE", "neo4j"),
        )

        yield client

        client.close()

    @pytest.fixture
    def repo(self, client: Neo4jClient) -> Neo4jGraphRepository:
        return Neo4jGraphRepository(client=client)

    @pytest.fixture(autouse=True)
    def cleanup(self, client: Neo4jClient) -> Generator[None, None, None]:
        yield

        client.run("MATCH (n:Concept) WHERE n.id STARTS WITH 'integ-' DETACH DELETE n")
        client.run("MATCH (p:CurriculumProfile) WHERE p.id STARTS WITH 'integ-' DELETE p")

    def test_persist_and_validate(
        self,
        repo: Neo4jGraphRepository,
    ) -> None:
        graph = _make_graph()

        repo.apply_schema()
        repo.persist(graph)
        repo.validate(graph)

    def test_persist_is_idempotent(
        self,
        repo: Neo4jGraphRepository,
    ) -> None:
        graph = _make_graph()

        repo.persist(graph)
        repo.persist(graph)
        repo.validate(graph)
    
    def test_persist_creates_expected_records_in_database(
        self,
        repo: Neo4jGraphRepository,
        client: Neo4jClient,
    ) -> None:
        graph = _make_graph()

        repo.apply_schema()
        repo.persist(graph)

        concept_count = client.run(
            """
            MATCH (n:Concept)
            WHERE n.id STARTS WITH 'integ-'
            RETURN count(n) AS count
            """
        )

        relationship_count = client.run(
            """
            MATCH (:Concept {id: 'integ-n1'})
                -[r:PREREQUISITE_OF {type: 'hard_prerequisite'}]->
                (:Concept {id: 'integ-n2'})
            RETURN count(r) AS count
            """
        )

        profile_count = client.run(
            """
            MATCH (p:CurriculumProfile {id: 'integ-p1'})
            RETURN count(p) AS count
            """
        )

        assert concept_count == [{"count": 2}]
        assert relationship_count == [{"count": 1}]
        assert profile_count == [{"count": 1}]