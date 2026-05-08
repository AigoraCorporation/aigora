from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .parser_errors import (
    GraphFileParseError,
    GraphFileReadError,
    GraphStructureError,
    UnsupportedGraphFileFormatError,
)


class GraphParser:
    SUPPORTED_EXTENSIONS = {".yaml", ".yml", ".json"}

    def parse_file(self, file_path: str | Path) -> dict[str, Any]:
        path = Path(file_path)
        self._validate_extension(path)

        raw_content = self._read_file(path)
        parsed_data = self._parse_content(path, raw_content)
        self._validate_top_level_structure(parsed_data)

        return parsed_data

    def _validate_extension(self, path: Path) -> None:
        if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedGraphFileFormatError(
                f"Unsupported graph file format: {path.suffix}"
            )

    def _read_file(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except OSError as exc:
            raise GraphFileReadError(
                f"Could not read graph file: {path}"
            ) from exc

    def _parse_content(self, path: Path, raw_content: str) -> dict[str, Any]:
        try:
            if path.suffix.lower() == ".json":
                parsed = json.loads(raw_content)
            else:
                parsed = yaml.safe_load(raw_content)
        except (json.JSONDecodeError, yaml.YAMLError) as exc:
            raise GraphFileParseError(
                f"Invalid or malformed graph file: {path.name}"
            ) from exc

        if parsed is None:
            raise GraphStructureError("Graph file is empty.")

        if not isinstance(parsed, dict):
            raise GraphStructureError(
                "Graph file root must be a dictionary/object."
            )

        return parsed

    def _validate_top_level_structure(self, parsed_data: dict[str, Any]) -> None:
        required_keys = {"nodes", "edges"}

        missing_keys = required_keys - parsed_data.keys()
        if missing_keys:
            missing = ", ".join(sorted(missing_keys))
            raise GraphStructureError(
                f"Graph file is missing required top-level keys: {missing}"
            )

        if not isinstance(parsed_data["nodes"], list):
            raise GraphStructureError("Top-level key 'nodes' must be a list.")

        if not isinstance(parsed_data["edges"], list):
            raise GraphStructureError("Top-level key 'edges' must be a list.")

        if "profiles" in parsed_data and not isinstance(parsed_data["profiles"], list):
            raise GraphStructureError("Top-level key 'profiles' must be a list.")