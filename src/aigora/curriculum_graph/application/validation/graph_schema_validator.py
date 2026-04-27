from __future__ import annotations

from typing import Any

from aigora.curriculum_graph.application.validation.schema_errors import SchemaValidationError

_VALID_EDGE_TYPES = {"hard_prerequisite", "soft_prerequisite", "regression_target"}
_VALID_MASTERY_LEVELS = {0, 1, 2, 3, 4, 5}


class GraphSchemaValidator:
    """Validates a parsed Curriculum Graph payload against the expected schema.

    This validator operates on raw Python dictionaries produced by the parser,
    enforcing field presence, field types, and allowed value shapes before
    the payload is handed off to the mapper.

    Pipeline position:
        file → parser → schema validation → mapper → domain
    """

    def validate(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            raise SchemaValidationError("Graph payload must be a dictionary.")

        self._validate_top_level(payload)
        self._validate_nodes(payload["nodes"])
        self._validate_edges(payload["edges"])
        self._validate_profiles(payload.get("profiles", []))

    # ── Top-level ─────────────────────────────────────────────────────────────

    def _validate_top_level(self, payload: dict[str, Any]) -> None:
        for required in ("nodes", "edges"):
            if required not in payload:
                raise SchemaValidationError(
                    f"Graph payload is missing required field: '{required}'."
                )

        if not isinstance(payload["nodes"], list):
            raise SchemaValidationError("Graph field 'nodes' must be a list.")

        if not isinstance(payload["edges"], list):
            raise SchemaValidationError("Graph field 'edges' must be a list.")

        profiles = payload.get("profiles")
        if profiles is not None and not isinstance(profiles, list):
            raise SchemaValidationError("Graph field 'profiles' must be a list.")

    # ── Nodes ─────────────────────────────────────────────────────────────────

    def _validate_nodes(self, nodes: list[Any]) -> None:
        for index, node in enumerate(nodes):
            self._validate_node(node, index)

    def _validate_node(self, node: Any, index: int) -> None:
        prefix = f"Node at index {index}"

        if not isinstance(node, dict):
            raise SchemaValidationError(f"{prefix} must be a dictionary.")

        for field in ("id", "name", "domain", "description"):
            if field not in node:
                raise SchemaValidationError(
                    f"{prefix} is missing required field: '{field}'."
                )
            if not isinstance(node[field], str):
                raise SchemaValidationError(
                    f"{prefix} field '{field}' must be a string."
                )

        if "mastery" not in node:
            raise SchemaValidationError(f"{prefix} is missing required field: 'mastery'.")

        self._validate_mastery(node["mastery"], prefix)

        for list_field in ("prerequisites", "regressions", "error_taxonomy"):
            value = node.get(list_field)
            if value is not None and not isinstance(value, list):
                raise SchemaValidationError(
                    f"{prefix} field '{list_field}' must be a list."
                )
            if isinstance(value, list):
                for item in value:
                    if not isinstance(item, str):
                        raise SchemaValidationError(
                            f"{prefix} field '{list_field}' must contain only strings."
                        )

    def _validate_mastery(self, mastery: Any, node_prefix: str) -> None:
        prefix = f"{node_prefix} mastery"

        if not isinstance(mastery, dict):
            raise SchemaValidationError(f"{prefix} must be a dictionary.")

        if "levels" not in mastery:
            raise SchemaValidationError(f"{prefix} is missing required field: 'levels'.")

        if not isinstance(mastery["levels"], list):
            raise SchemaValidationError(f"{prefix} field 'levels' must be a list.")

        for level_index, level_entry in enumerate(mastery["levels"]):
            self._validate_mastery_level(level_entry, f"{prefix} level at index {level_index}")

    def _validate_mastery_level(self, entry: Any, prefix: str) -> None:
        if not isinstance(entry, dict):
            raise SchemaValidationError(f"{prefix} must be a dictionary.")

        if "level" not in entry:
            raise SchemaValidationError(f"{prefix} is missing required field: 'level'.")

        if not isinstance(entry["level"], int):
            raise SchemaValidationError(f"{prefix} field 'level' must be an integer.")

        if entry["level"] not in _VALID_MASTERY_LEVELS:
            raise SchemaValidationError(
                f"{prefix} field 'level' has invalid value: {entry['level']}. "
                f"Allowed values: {sorted(_VALID_MASTERY_LEVELS)}."
            )

        if "description" not in entry:
            raise SchemaValidationError(f"{prefix} is missing required field: 'description'.")

        if not isinstance(entry["description"], str):
            raise SchemaValidationError(f"{prefix} field 'description' must be a string.")

    # ── Edges ─────────────────────────────────────────────────────────────────

    def _validate_edges(self, edges: list[Any]) -> None:
        for index, edge in enumerate(edges):
            self._validate_edge(edge, index)

    def _validate_edge(self, edge: Any, index: int) -> None:
        prefix = f"Edge at index {index}"

        if not isinstance(edge, dict):
            raise SchemaValidationError(f"{prefix} must be a dictionary.")

        for field in ("type", "source", "target"):
            if field not in edge:
                raise SchemaValidationError(
                    f"{prefix} is missing required field: '{field}'."
                )
            if not isinstance(edge[field], str):
                raise SchemaValidationError(
                    f"{prefix} field '{field}' must be a string."
                )

        if edge["type"] not in _VALID_EDGE_TYPES:
            raise SchemaValidationError(
                f"{prefix} field 'type' has invalid value: {edge['type']!r}. "
                f"Allowed values: {sorted(_VALID_EDGE_TYPES)}."
            )

    # ── Profiles ──────────────────────────────────────────────────────────────

    def _validate_profiles(self, profiles: list[Any]) -> None:
        for index, profile in enumerate(profiles):
            self._validate_profile(profile, index)

    def _validate_profile(self, profile: Any, index: int) -> None:
        prefix = f"Profile at index {index}"

        if not isinstance(profile, dict):
            raise SchemaValidationError(f"{prefix} must be a dictionary.")

        for field in ("id", "name"):
            if field not in profile:
                raise SchemaValidationError(
                    f"{prefix} is missing required field: '{field}'."
                )
            if not isinstance(profile[field], str):
                raise SchemaValidationError(
                    f"{prefix} field '{field}' must be a string."
                )

        for list_field in ("required_nodes", "progression_path", "exam_skill_overlay"):
            value = profile.get(list_field)
            if value is not None and not isinstance(value, list):
                raise SchemaValidationError(
                    f"{prefix} field '{list_field}' must be a list."
                )
            if isinstance(value, list):
                for item in value:
                    if not isinstance(item, str):
                        raise SchemaValidationError(
                            f"{prefix} field '{list_field}' must contain only strings."
                        )

        for dict_field in ("mastery_targets", "node_weights"):
            value = profile.get(dict_field)
            if value is not None and not isinstance(value, dict):
                raise SchemaValidationError(
                    f"{prefix} field '{dict_field}' must be a dictionary."
                )

        mastery_targets = profile.get("mastery_targets")
        if isinstance(mastery_targets, dict):
            for node_id, level in mastery_targets.items():
                if not isinstance(node_id, str):
                    raise SchemaValidationError(
                        f"{prefix} field 'mastery_targets' keys must be strings."
                    )
                if not isinstance(level, int):
                    raise SchemaValidationError(
                        f"{prefix} field 'mastery_targets' values must be integers."
                    )
                if level not in _VALID_MASTERY_LEVELS:
                    raise SchemaValidationError(
                        f"{prefix} field 'mastery_targets' has invalid level: {level}."
                    )

        node_weights = profile.get("node_weights")
        if isinstance(node_weights, dict):
            for node_id, weight in node_weights.items():
                if not isinstance(node_id, str):
                    raise SchemaValidationError(
                        f"{prefix} field 'node_weights' keys must be strings."
                    )
                if not isinstance(weight, (int, float)):
                    raise SchemaValidationError(
                        f"{prefix} field 'node_weights' values must be numbers."
                    )
