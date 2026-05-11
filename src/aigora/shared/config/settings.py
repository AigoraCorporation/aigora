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
class Settings:
    neo4j: Neo4jSettings

    @classmethod
    def from_env(cls) -> Settings:
        return cls(neo4j=Neo4jSettings.from_env())


__all__ = ["Neo4jSettings", "Settings"]
