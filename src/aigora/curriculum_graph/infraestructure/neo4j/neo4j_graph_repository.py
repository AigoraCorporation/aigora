from __future__ import annotations

import os
from pathlib import Path

from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.enums import MasteryLevel
from aigora.curriculum_graph.infraestructure.neo4j.neo4j_client import Neo4jClient

_CYPHER_DIR = Path(__file__).parent / "cypher"

_DEFAULT_BATCH_SIZE = int(os.environ.get("NEO4J_DEFAULT_BATCH_SIZE", "500"))


def _load_cypher(filename: str) -> str:
    return (_CYPHER_DIR / filename).read_text(encoding="utf-8")


class Neo4jGraphRepository:
    """Neo4j implementation of the GraphRepository port.

    Persists CurriculumGraph data using batched UNWIND/MERGE operations.
    All write operations are idempotent — safe to run multiple times with
    the same graph without creating duplicate data.
    """

    def __init__(
        self,
        client: Neo4jClient,
        batch_size: int = _DEFAULT_BATCH_SIZE,
    ) -> None:
        self._client = client
        self._batch_size = batch_size

    # ------------------------------------------------------------------
    # GraphRepository port implementation
    # ------------------------------------------------------------------

    def apply_schema(self) -> None:
        """Apply Neo4j constraints and indexes from centralized Cypher files."""
        for statement in self._iter_statements(_load_cypher("constraints.cypher")):
            self._client.run(statement)
        for statement in self._iter_statements(_load_cypher("indexes.cypher")):
            self._client.run(statement)

    def persist(self, graph: CurriculumGraph) -> None:
        """Persist all nodes, edges, and profiles from the graph.

        Uses batched UNWIND/MERGE to ensure idempotency.
        """
        self._persist_nodes(graph)
        self._persist_edges(graph)
        self._persist_profiles(graph)

    def validate(self, graph: CurriculumGraph) -> None:
        """Validate persisted state against in-memory graph.

        Raises ValueError if node count, edge count, or required IDs
        do not match the in-memory graph.
        """
        self._validate_node_count(graph)
        self._validate_edge_count(graph)
        self._validate_required_node_ids(graph)
        self._validate_profile_consistency(graph)

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _persist_nodes(self, graph: CurriculumGraph) -> None:
        nodes = [
            {
                "id": node.id,
                "name": node.name,
                "domain": node.domain,
                "description": node.description,
            }
            for node in graph.nodes.values()
        ]
        for batch in self._batches(nodes):
            self._client.run(
                """
                UNWIND $rows AS row
                MERGE (n:Concept {id: row.id})
                SET n.name = row.name,
                    n.domain = row.domain,
                    n.description = row.description
                """,
                {"rows": batch},
            )

    def _persist_edges(self, graph: CurriculumGraph) -> None:
        edges = [
            {"source": edge.source, "target": edge.target, "type": edge.type.value}
            for edge in graph.edges
        ]
        for batch in self._batches(edges):
            self._client.run(
                """
                UNWIND $rows AS row
                MATCH (src:Concept {id: row.source})
                MATCH (tgt:Concept {id: row.target})
                MERGE (src)-[r:RELATED {type: row.type}]->(tgt)
                """,
                {"rows": batch},
            )

    def _persist_profiles(self, graph: CurriculumGraph) -> None:
        profiles = [
            {
                "id": profile.id,
                "name": profile.name,
                "required_nodes": list(profile.required_nodes),
                "mastery_targets": {
                    k: v.value for k, v in profile.mastery_targets.items()
                },
                "node_weights": dict(profile.node_weights),
                "progression_path": list(profile.progression_path),
            }
            for profile in graph.profiles.values()
        ]
        for batch in self._batches(profiles):
            self._client.run(
                """
                UNWIND $rows AS row
                MERGE (p:CurriculumProfile {id: row.id})
                SET p.name = row.name,
                    p.required_nodes = row.required_nodes,
                    p.node_weights = row.node_weights,
                    p.progression_path = row.progression_path
                """,
                {"rows": batch},
            )

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def _validate_node_count(self, graph: CurriculumGraph) -> None:
        result = self._client.run("MATCH (n:Concept) RETURN count(n) AS cnt")
        persisted = result[0]["cnt"]
        expected = len(graph.nodes)
        if persisted < expected:
            raise ValueError(
                f"Node count mismatch: expected {expected}, found {persisted}"
            )

    def _validate_edge_count(self, graph: CurriculumGraph) -> None:
        result = self._client.run("MATCH ()-[r:RELATED]->() RETURN count(r) AS cnt")
        persisted = result[0]["cnt"]
        expected = len(graph.edges)
        if persisted < expected:
            raise ValueError(
                f"Edge count mismatch: expected {expected}, found {persisted}"
            )

    def _validate_required_node_ids(self, graph: CurriculumGraph) -> None:
        expected_ids = list(graph.nodes.keys())
        result = self._client.run(
            "UNWIND $ids AS id MATCH (n:Concept {id: id}) RETURN n.id AS found",
            {"ids": expected_ids},
        )
        found_ids = {row["found"] for row in result}
        missing = set(expected_ids) - found_ids
        if missing:
            raise ValueError(f"Missing persisted node IDs: {missing}")

    def _validate_profile_consistency(self, graph: CurriculumGraph) -> None:
        expected_ids = list(graph.profiles.keys())
        if not expected_ids:
            return
        result = self._client.run(
            "UNWIND $ids AS id MATCH (p:CurriculumProfile {id: id}) RETURN p.id AS found",
            {"ids": expected_ids},
        )
        found_ids = {row["found"] for row in result}
        missing = set(expected_ids) - found_ids
        if missing:
            raise ValueError(f"Missing persisted profile IDs: {missing}")

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def _batches(self, items: list) -> list[list]:
        return [
            items[i: i + self._batch_size]
            for i in range(0, len(items), self._batch_size)
        ] or [[]]

    @staticmethod
    def _iter_statements(cypher: str) -> list[str]:
        """Split a Cypher file into individual statements (split on ';')."""
        return [
            s.strip()
            for s in cypher.split(";")
            if s.strip() and not s.strip().startswith("//")
        ]
