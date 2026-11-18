from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Neo4jSettings:
    uri: str
    username: str
    password: str
    database: str = "neo4j"
    default_batch_size: int = 500

    @classmethod
    def from_env(cls) -> Neo4jSettings:
        return cls(
            uri=os.environ["NEO4J_URI"],
            username=os.environ["NEO4J_USERNAME"],
            password=os.environ["NEO4J_PASSWORD"],
            database=os.environ.get("NEO4J_DATABASE", "neo4j"),
            default_batch_size=int(os.environ.get("NEO4J_DEFAULT_BATCH_SIZE", "500")),
        )


@dataclass(frozen=True)
class GrpcServerSettings:
    """Runtime settings of the Curriculum Graph gRPC API (ADR-007)."""

    port: int = 50051
    max_workers: int = 10
    required_graph_version: str | None = None
    load_retry_seconds: float = 5.0

    @classmethod
    def from_env(cls) -> GrpcServerSettings:
        return cls(
            port=int(os.environ.get("GRPC_PORT", "50051")),
            max_workers=int(os.environ.get("GRPC_MAX_WORKERS", "10")),
            required_graph_version=os.environ.get("GRAPH_VERSION_DEFAULT") or None,
            load_retry_seconds=float(os.environ.get("GRAPH_LOAD_RETRY_SECONDS", "5")),
        )


@dataclass(frozen=True)
class Settings:
    neo4j: Neo4jSettings

    @classmethod
    def from_env(cls) -> Settings:
        return cls(neo4j=Neo4jSettings.from_env())


__all__ = ["GrpcServerSettings", "Neo4jSettings", "Settings"]
