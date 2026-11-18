"""Unit tests for Neo4jCurriculumGraphReader with a fake client.

The round-trip test feeds the reader with exactly the rows the repository
writes, proving publication is lossless for the read side (ADR-007).
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from aigora.curriculum_graph.application.errors.read_graph_errors import GraphUnavailableError
from aigora.curriculum_graph.infrastructure.neo4j.errors import Neo4jClientError
from aigora.curriculum_graph.infrastructure.neo4j.neo4j_curriculum_graph_reader import Neo4jCurriculumGraphReader
from aigora.curriculum_graph.infrastructure.neo4j.neo4j_curriculum_graph_repository import (
    Neo4jCurriculumGraphRepository,
)
from tests.fixtures.curriculum_graph.read_graph import GRAPH_VERSION, make_graph


def _written_rows(graph):
    client = MagicMock()
    client.run.return_value = []
    Neo4jCurriculumGraphRepository(client=client, batch_size=1000).persist(graph)
    calls = [c.args for c in client.run.call_args_list]
    nodes, edges, profiles = (call[1]["rows"] for call in calls[:3])
    metadata = calls[3][1]
    return nodes, edges, profiles, metadata


def _reader_for(nodes, edges, profiles, version) -> Neo4jCurriculumGraphReader:
    client = MagicMock()
    client.run.side_effect = [
        [{"graph_version": version}] if version is not None else [],
        nodes,
        [{"source": e["source"], "target": e["target"], "type": e["type"]} for e in edges],
        profiles,
    ]
    return Neo4jCurriculumGraphReader(client)


def test_round_trip_rebuilds_published_graph() -> None:
    original = make_graph()
    nodes, edges, profiles, metadata = _written_rows(original)
    assert metadata["graph_version"] == GRAPH_VERSION
    assert all(row["graph_version"] == GRAPH_VERSION for row in [*nodes, *edges, *profiles])

    rebuilt = _reader_for(nodes, edges, profiles, GRAPH_VERSION).load_published()

    assert rebuilt.version == original.version
    assert rebuilt.nodes.keys() == original.nodes.keys()
    for node_id, node in original.nodes.items():
        copy = rebuilt.nodes[node_id]
        assert copy.mastery_criteria == node.mastery_criteria
        assert copy.error_taxonomy == node.error_taxonomy
        assert copy.regression_ids == node.regression_ids
        assert (copy.name, copy.domain, copy.description) == (node.name, node.domain, node.description)
    assert {(e.type, e.source, e.target) for e in rebuilt.edges} == {
        (e.type, e.source, e.target) for e in original.edges
    }
    profile, copy = original.profiles["profile.core"], rebuilt.profiles["profile.core"]
    assert copy.required_nodes == profile.required_nodes
    assert copy.mastery_targets == profile.mastery_targets
    assert copy.node_weights == profile.node_weights
    assert copy.progression_path == profile.progression_path
    assert copy.exam_skill_overlay == profile.exam_skill_overlay


def test_persisted_mastery_is_json_ordered_by_level() -> None:
    nodes, *_ = _written_rows(make_graph())
    criteria = json.loads(nodes[0]["mastery_criteria_json"])
    assert [c["level"] for c in criteria] == [1, 3]


def test_no_metadata_means_unavailable() -> None:
    with pytest.raises(GraphUnavailableError, match="No published"):
        _reader_for([], [], [], None).load_published()


def test_client_failure_means_unavailable_without_leaking_details() -> None:
    client = MagicMock()
    client.run.side_effect = Neo4jClientError("Query execution failed: bolt://secret-host refused")
    with pytest.raises(GraphUnavailableError) as exc:
        Neo4jCurriculumGraphReader(client).load_published()
    assert "secret-host" not in exc.value.message


def test_legacy_publication_without_mastery_is_unavailable() -> None:
    nodes, edges, profiles, _ = _written_rows(make_graph())
    for row in nodes:
        row.pop("mastery_criteria_json")
    with pytest.raises(GraphUnavailableError, match="republish"):
        _reader_for(nodes, edges, profiles, GRAPH_VERSION).load_published()


def test_empty_snapshot_is_unavailable() -> None:
    with pytest.raises(GraphUnavailableError):
        _reader_for([], [], [], GRAPH_VERSION).load_published()
