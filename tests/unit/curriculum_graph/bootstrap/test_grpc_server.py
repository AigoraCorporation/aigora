"""Unit tests for the composition root's background snapshot loading."""
from __future__ import annotations

import json
import logging
import time

from aigora.curriculum_graph.bootstrap.grpc_server import start_server
from aigora.curriculum_graph.bootstrap.logging_config import JsonLogFormatter, configure_logging
from aigora.shared.config.settings import GrpcServerSettings
from tests.fixtures.curriculum_graph.read_graph import GRAPH_VERSION, StaticGraphReader


def _wait_until(predicate, timeout: float = 2.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)
    return False


def test_server_starts_not_ready_and_loads_when_store_recovers() -> None:
    reader = StaticGraphReader(fail=True)
    running = start_server(reader, GrpcServerSettings(port=0, load_retry_seconds=0.02), host="127.0.0.1")
    try:
        assert not running.provider.is_ready
        reader.fail = False
        assert _wait_until(lambda: running.provider.is_ready)
        assert running.provider.graph_version == GRAPH_VERSION
        assert reader.calls >= 2
    finally:
        running.stop(grace=None)


def test_stop_ends_retry_loop() -> None:
    reader = StaticGraphReader(fail=True)
    running = start_server(reader, GrpcServerSettings(port=0, load_retry_seconds=0.02), host="127.0.0.1")
    running.stop(grace=None)
    calls = reader.calls
    time.sleep(0.1)
    assert reader.calls <= calls + 1


def test_settings_from_env(monkeypatch) -> None:
    monkeypatch.setenv("GRPC_PORT", "6000")
    monkeypatch.setenv("GRAPH_VERSION_DEFAULT", "2026.11.0")
    monkeypatch.delenv("GRPC_MAX_WORKERS", raising=False)
    settings = GrpcServerSettings.from_env()
    assert (settings.port, settings.max_workers, settings.required_graph_version) == (6000, 10, "2026.11.0")


def test_json_formatter_includes_extras_and_exceptions() -> None:
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.getLogger("t").makeRecord(
            "t", logging.ERROR, __file__, 1, "evt", None, exc_info=__import__("sys").exc_info(), extra={"port": 1}
        )
    payload = json.loads(JsonLogFormatter().format(record))
    assert payload["event"] == "evt" and payload["port"] == 1 and "ValueError: boom" in payload["exception"]


def test_configure_logging_installs_json_handler() -> None:
    root = logging.getLogger()
    previous = root.handlers[:], root.level
    try:
        configure_logging("DEBUG")
        assert isinstance(root.handlers[0].formatter, JsonLogFormatter) and root.level == logging.DEBUG
    finally:
        root.handlers[:], _ = previous
        root.setLevel(previous[1])
