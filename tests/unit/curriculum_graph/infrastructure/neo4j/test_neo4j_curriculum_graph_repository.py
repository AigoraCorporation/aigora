"""Unit tests for Neo4jCurriculumGraphRepository.

Uses a mock Neo4jClient to avoid requiring a live database.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.entities.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.entities.edge import Edge
from aigora.curriculum_graph.domain.enums.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.value_objects.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.entities.node import Node
from aigora.curriculum_graph.infrastructure.neo4j.neo4j_curriculum_graph_repository import (
    Neo4jCurriculumGraphRepository,
)


def _make_node(node_id: str = "n1") -> Node:
    return Node(
        id=node_id,
        name=f"Node {node_id}",
        domain="math",
        description="A test node",
        mastery_criteria=MasteryScale(
            criteria_by_level={
                MasteryLevel.GUIDED: MasteryCriterion(
                    level=MasteryLevel.GUIDED, description="Guided"
                )
            }
        ),
    )


def _make_graph() -> CurriculumGraph:
    graph = CurriculumGraph()
    n1 = _make_node("n1")
    n2 = _make_node("n2")
    graph.add_node(n1)
    graph.add_node(n2)
    graph.add_edge(Edge(type=EdgeType.HARD_PREREQUISITE, source="n1", target="n2"))
    profile = CurriculumProfile(
        id="p1",
        name="Profile 1",
        required_nodes={"n1", "n2"},
    )
    graph.add_profile(profile)
    return graph


class TestNeo4jCurriculumGraphRepositoryUnit:
    @pytest.fixture
    def mock_client(self) -> MagicMock:
        client = MagicMock()
        client.run.return_value = []
        return client

    @pytest.fixture
    def repo(self, mock_client: MagicMock) -> Neo4jCurriculumGraphRepository:
        return Neo4jCurriculumGraphRepository(client=mock_client, batch_size=100)

    def test_persist_calls_run_for_nodes(
        self, repo: Neo4jCurriculumGraphRepository, mock_client: MagicMock
    ) -> None:
        graph = _make_graph()
        repo._persist_nodes(graph)
        mock_client.run.assert_called_once()
        call_args = mock_client.run.call_args
        rows = call_args[1]["rows"] if call_args[1] else call_args[0][1]["rows"]
        assert any(r["id"] == "n1" for r in rows)
        assert any(r["id"] == "n2" for r in rows)

    def test_persist_calls_run_for_edges(
        self, repo: Neo4jCurriculumGraphRepository, mock_client: MagicMock
    ) -> None:
        graph = _make_graph()
        repo._persist_edges(graph)
        mock_client.run.assert_called_once()
        call_args = mock_client.run.call_args
        rows = call_args[1]["rows"] if call_args[1] else call_args[0][1]["rows"]
        assert rows[0]["source"] == "n1"
        assert rows[0]["target"] == "n2"
        assert rows[0]["type"] == EdgeType.HARD_PREREQUISITE.value

    def test_persist_calls_run_for_profiles(
        self, repo: Neo4jCurriculumGraphRepository, mock_client: MagicMock
    ) -> None:
        graph = _make_graph()
        repo._persist_profiles(graph)
        mock_client.run.assert_called_once()
        call_args = mock_client.run.call_args
        rows = call_args[1]["rows"] if call_args[1] else call_args[0][1]["rows"]
        assert rows[0]["id"] == "p1"

    def test_persist_full_pipeline(
        self, repo: Neo4jCurriculumGraphRepository, mock_client: MagicMock
    ) -> None:
        graph = _make_graph()
        repo.persist(graph)
        assert mock_client.run.call_count == 3  # nodes, edges, profiles

    def test_validate_delegates_to_persistence_validator(
        self, repo: Neo4jCurriculumGraphRepository, mock_client: MagicMock
    ) -> None:
        graph = _make_graph()
        mock_client.run.side_effect = [
            [{"node_count": 2}],
            [{"edge_count": 1}],
            [{"found_id": "n1"}, {"found_id": "n2"}],
            [{"found_id": "p1"}],
        ]
        repo.validate(graph)  # Must not raise

    def test_batches_splits_correctly(self, repo: Neo4jCurriculumGraphRepository) -> None:
        items = list(range(250))
        batches = repo._batches(items)
        assert len(batches) == 3  # 100, 100, 50

    def test_batches_empty_list_returns_one_empty_batch(
        self, repo: Neo4jCurriculumGraphRepository
    ) -> None:
        assert repo._batches([]) == [[]]
