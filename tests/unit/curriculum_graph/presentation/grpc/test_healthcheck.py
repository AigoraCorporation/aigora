"""Unit tests for the container health probe."""
from __future__ import annotations

from aigora.curriculum_graph.bootstrap.grpc_server import start_server
from aigora.curriculum_graph.presentation.grpc import healthcheck
from aigora.shared.config.settings import GrpcServerSettings
from tests.fixtures.curriculum_graph.read_graph import StaticGraphReader


def _target(running) -> str:
    return f"127.0.0.1:{running.port}"


def test_probe_succeeds_only_when_serving() -> None:
    ready = start_server(StaticGraphReader(), GrpcServerSettings(port=0), host="127.0.0.1")
    not_ready = start_server(
        StaticGraphReader(fail=True), GrpcServerSettings(port=0, load_retry_seconds=60), host="127.0.0.1"
    )
    try:
        assert healthcheck.main(["--target", _target(ready)]) == 0
        assert healthcheck.main(["--target", _target(not_ready)]) == 1
    finally:
        ready.stop(grace=None)
        not_ready.stop(grace=None)


def test_probe_fails_when_nothing_listens() -> None:
    assert healthcheck.probe("127.0.0.1:1", timeout=0.5) is False
