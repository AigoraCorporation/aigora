from __future__ import annotations

import pytest

from aigora.curriculum_graph.application.errors.read_graph_errors import (
    GraphUnavailableError,
    GraphVersionMismatchError,
)
from aigora.curriculum_graph.application.services.published_graph_provider import PublishedGraphProvider
from tests.fixtures.curriculum_graph.read_graph import GRAPH_VERSION, StaticGraphReader, make_graph


def test_snapshot_before_load_is_unavailable() -> None:
    provider = PublishedGraphProvider(StaticGraphReader())
    assert not provider.is_ready
    with pytest.raises(GraphUnavailableError):
        provider.snapshot()


def test_load_serves_published_graph() -> None:
    provider = PublishedGraphProvider(StaticGraphReader())
    assert provider.load() is True
    assert provider.is_ready
    assert provider.graph_version == GRAPH_VERSION
    assert provider.snapshot().version == GRAPH_VERSION
    assert provider.snapshot(GRAPH_VERSION).version == GRAPH_VERSION


def test_expected_version_mismatch_is_rejected_without_echoing_version() -> None:
    provider = PublishedGraphProvider(StaticGraphReader())
    provider.load()
    with pytest.raises(GraphVersionMismatchError) as exc:
        provider.snapshot("1999.01.0")
    assert exc.value.graph_version is None


def test_failed_load_keeps_provider_unavailable_and_records_reason() -> None:
    provider = PublishedGraphProvider(StaticGraphReader(fail=True))
    assert provider.load() is False
    assert not provider.is_ready
    assert provider.last_error == "The graph store is unreachable."


def test_failed_reload_drops_previous_snapshot() -> None:
    reader = StaticGraphReader()
    provider = PublishedGraphProvider(reader)
    provider.load()
    reader.fail = True
    assert provider.load() is False
    assert not provider.is_ready


def test_required_version_mismatch_prevents_serving() -> None:
    provider = PublishedGraphProvider(StaticGraphReader(), required_version="2025.01.0")
    assert provider.load() is False
    assert "does not match the required version" in (provider.last_error or "")


def test_graph_without_version_is_not_served() -> None:
    provider = PublishedGraphProvider(StaticGraphReader(make_graph(version=None)))
    assert provider.load() is False
