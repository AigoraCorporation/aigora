"""Composition root and entry point of the Curriculum Graph gRPC API (ADR-007).

This is the only module that wires infrastructure adapters into application
use cases and the gRPC delivery adapter.

Run with:  python -m aigora.curriculum_graph.bootstrap
"""
from __future__ import annotations

import logging
import signal
import threading
from concurrent import futures
from dataclasses import dataclass

import grpc

from aigora.curriculum_graph.application.ports.curriculum_graph_reader import CurriculumGraphReader
from aigora.curriculum_graph.application.services.published_graph_provider import PublishedGraphProvider
from aigora.curriculum_graph.application.use_cases.read_graph import ReadGraphUseCase
from aigora.curriculum_graph.presentation.grpc import CurriculumGraphServicer, register
from aigora.shared.config.settings import GrpcServerSettings

logger = logging.getLogger("aigora.curriculum_graph.grpc")


@dataclass
class RunningServer:
    server: grpc.Server
    port: int
    provider: PublishedGraphProvider
    loader: GraphLoader

    def stop(self, grace: float | None = 5.0) -> None:
        self.loader.stop()
        self.server.stop(grace).wait()


class GraphLoader:
    """Loads the published snapshot, retrying in the background until it succeeds."""

    def __init__(self, provider: PublishedGraphProvider, retry_seconds: float) -> None:
        self._provider = provider
        self._retry_seconds = retry_seconds
        self._stopped = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._attempt():
            return
        self._thread = threading.Thread(target=self._retry_loop, name="graph-loader", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stopped.set()

    def _attempt(self) -> bool:
        if self._provider.load():
            logger.info("graph_loaded", extra={"graph_version": self._provider.graph_version})
            return True
        logger.warning("graph_load_failed", extra={"reason": self._provider.last_error})
        return False

    def _retry_loop(self) -> None:
        while not self._stopped.wait(self._retry_seconds):
            if self._attempt():
                return


def start_server(
    reader: CurriculumGraphReader,
    settings: GrpcServerSettings,
    *,
    host: str = "[::]",
) -> RunningServer:
    """Build, wire and start the gRPC server. Returns once the port is bound."""
    provider = PublishedGraphProvider(reader, required_version=settings.required_graph_version)
    use_case = ReadGraphUseCase(provider)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=settings.max_workers))
    register(server, CurriculumGraphServicer(use_case, provider))
    port = server.add_insecure_port(f"{host}:{settings.port}")
    if port == 0:
        raise RuntimeError(f"Could not bind gRPC port {settings.port}")
    server.start()
    loader = GraphLoader(provider, settings.load_retry_seconds)
    loader.start()
    logger.info("grpc_server_started", extra={"port": port})
    return RunningServer(server=server, port=port, provider=provider, loader=loader)


def main() -> None:
    from aigora.curriculum_graph.infrastructure.neo4j import Neo4jClient, Neo4jCurriculumGraphReader

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    settings = GrpcServerSettings.from_env()
    client = Neo4jClient()
    running = start_server(Neo4jCurriculumGraphReader(client), settings)

    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    stop.wait()
    logger.info("grpc_server_stopping")
    running.stop()
    client.close()


if __name__ == "__main__":
    main()
