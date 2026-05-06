from __future__ import annotations

import os
from pathlib import Path
import json

from aigora.curriculum_graph.application.graph_persistence_validator import (
    GraphPersistenceValidationError,
    GraphPersistenceValidator,
    PersistenceValidationResult,
)
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.enums import MasteryLevel
from aigora.curriculum_graph.infrastructure.neo4j.neo4j_client import Neo4jClient

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

        Loads validation Cypher from validations.cypher, queries the
        database for counts and IDs, then delegates evaluation to
        GraphPersistenceValidator.

        Raises:
            GraphPersistenceValidationError: If persisted state does not
                match the in-memory graph.
        """
        queries = self._iter_statements(_load_cypher("validations.cypher"))
        node_count_q, edge_count_q, node_ids_q, profile_ids_q = queries

        node_count = self._client.run(node_count_q)[0]["node_count"]
        edge_count = self._client.run(edge_count_q)[0]["edge_count"]

        expected_node_ids = list(graph.nodes.keys())
        found_node_rows = self._client.run(node_ids_q, {"ids": expected_node_ids})
        found_node_ids = {row["found_id"] for row in found_node_rows}

        expected_profile_ids = list(graph.profiles.keys())
        found_profile_ids: set[str] = set()
        if expected_profile_ids:
            found_profile_rows = self._client.run(
                profile_ids_q, {"ids": expected_profile_ids}
            )
            found_profile_ids = {row["found_id"] for row in found_profile_rows}

        result = PersistenceValidationResult(
            persisted_node_count=node_count,
            persisted_edge_count=edge_count,
            found_node_ids=found_node_ids,
            found_profile_ids=found_profile_ids,
        )
        GraphPersistenceValidator().validate(graph, result)

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
                MERGE (src)-[r:PREREQUISITE_OF]->(tgt)
                SET r.type = row.type
                """,
                {"rows": batch},
            )

    def _persist_profiles(self, graph: CurriculumGraph) -> None:
        profiles = [
            {
                "id": profile.id,
                "name": profile.name,
                "required_nodes": list(profile.required_nodes),
                "mastery_targets_json": json.dumps(
                    {k: v.value for k, v in profile.mastery_targets.items()}
                ),
                "node_weights_json": json.dumps(dict(profile.node_weights)),
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
                    p.mastery_targets_json = row.mastery_targets_json,
                    p.node_weights_json = row.node_weights_json,
                    p.progression_path = row.progression_path
                """,
                {"rows": batch},
            )

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
        """Split a Cypher file into individual statements (split on ';').

        Single-line // comments are stripped from each statement block.
        Empty blocks and comment-only blocks are skipped.
        """
        statements = []
        for piece in cypher.split(";"):
            non_comment_lines = [
                line
                for line in piece.splitlines()
                if line.strip() and not line.strip().startswith("//")
            ]
            statement = "\n".join(non_comment_lines).strip()
            if statement:
                statements.append(statement)
        return statements
