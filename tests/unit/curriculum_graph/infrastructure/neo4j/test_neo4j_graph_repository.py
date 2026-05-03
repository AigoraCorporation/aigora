"""Unit tests for Neo4jGraphRepository.

Uses a mock Neo4jClient to avoid requiring a live database.
"""
from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.node import Node
from aigora.curriculum_graph.infraestructure.neo4j.neo4j_graph_repository import (
    Neo4jGraphRepository,
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


class TestNeo4jGraphRepositoryUnit:
    @pytest.fixture
    def mock_client(self) -> MagicMock:
        client = MagicMock()
        client.run.return_value = []
        return client

    @pytest.fixture
    def repo(self, mock_client: MagicMock) -> Neo4jGraphRepository:
        return Neo4jGraphRepository(client=mock_client, batch_size=100)

    def test_persist_calls_run_for_nodes(
        self, repo: Neo4jGraphRepository, mock_client: MagicMock
    ) -> None:
        graph = _make_graph()
        repo._persist_nodes(graph)
        mock_client.run.assert_called_once()
        call_args = mock_client.run.call_args
        rows = call_args[1]["rows"] if call_args[1] else call_args[0][1]["rows"]
        assert any(r["id"] == "n1" for r in rows)
        assert any(r["id"] == "n2" for r in rows)

    def test_persist_calls_run_for_edges(
        self, repo: Neo4jGraphRepository, mock_client: MagicMock
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
        self, repo: Neo4jGraphRepository, mock_client: MagicMock
    ) -> None:
        graph = _make_graph()
        repo._persist_profiles(graph)
        mock_client.run.assert_called_once()
        call_args = mock_client.run.call_args
        rows = call_args[1]["rows"] if call_args[1] else call_args[0][1]["rows"]
        assert rows[0]["id"] == "p1"

    def test_persist_full_pipeline(
        self, repo: Neo4jGraphRepository, mock_client: MagicMock
    ) -> None:
        graph = _make_graph()
        repo.persist(graph)
        assert mock_client.run.call_count == 3  # nodes, edges, profiles

    def test_validate_raises_on_node_count_mismatch(
        self, repo: Neo4jGraphRepository, mock_client: MagicMock
    ) -> None:
        graph = _make_graph()
        # Simulate persisted count < expected
        mock_client.run.side_effect = [
            [{"cnt": 0}],  # node count
        ]
        with pytest.raises(ValueError, match="Node count mismatch"):
            repo._validate_node_count(graph)

    def test_validate_raises_on_missing_profile(
        self, repo: Neo4jGraphRepository, mock_client: MagicMock
    ) -> None:
        graph = _make_graph()
        mock_client.run.return_value = []  # no profiles found
        with pytest.raises(ValueError, match="Missing persisted profile IDs"):
            repo._validate_profile_consistency(graph)

    def test_batches_splits_correctly(self, repo: Neo4jGraphRepository) -> None:
        items = list(range(250))
        batches = repo._batches(items)
        assert len(batches) == 3  # 100, 100, 50

    def test_batches_empty_list_returns_one_empty_batch(
        self, repo: Neo4jGraphRepository
    ) -> None:
        assert repo._batches([]) == [[]]
