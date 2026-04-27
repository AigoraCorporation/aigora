from pathlib import Path

import pytest

from aigora.curriculum_graph.application.parsing.graph_parser import GraphParser
from aigora.curriculum_graph.application.parsing.parser_errors import (
    GraphFileParseError,
    GraphFileReadError,
    GraphStructureError,
    UnsupportedGraphFileFormatError,
)


def test_should_parse_valid_json_file(tmp_path: Path):
    file_path = tmp_path / "graph.json"
    file_path.write_text(
        """
        {
          "nodes": [],
          "edges": [],
          "profiles": []
        }
        """,
        encoding="utf-8",
    )

    parser = GraphParser()
    result = parser.parse_file(file_path)

    assert result == {
        "nodes": [],
        "edges": [],
        "profiles": [],
    }


def test_should_parse_valid_yaml_file(tmp_path: Path):
    file_path = tmp_path / "graph.yaml"
    file_path.write_text(
        """
        nodes: []
        edges: []
        profiles: []
        """,
        encoding="utf-8",
    )

    parser = GraphParser()
    result = parser.parse_file(file_path)

    assert result == {
        "nodes": [],
        "edges": [],
        "profiles": [],
    }


def test_should_raise_error_for_unsupported_extension(tmp_path: Path):
    file_path = tmp_path / "graph.txt"
    file_path.write_text("nodes: []", encoding="utf-8")

    parser = GraphParser()

    with pytest.raises(UnsupportedGraphFileFormatError):
        parser.parse_file(file_path)


def test_should_raise_error_when_file_does_not_exist():
    parser = GraphParser()

    with pytest.raises(GraphFileReadError):
        parser.parse_file("missing.yaml")


def test_should_raise_error_for_malformed_json(tmp_path: Path):
    file_path = tmp_path / "graph.json"
    file_path.write_text('{ "nodes": [}', encoding="utf-8")

    parser = GraphParser()

    with pytest.raises(GraphFileParseError):
        parser.parse_file(file_path)


def test_should_raise_error_when_root_is_not_object(tmp_path: Path):
    file_path = tmp_path / "graph.json"
    file_path.write_text('["not-an-object"]', encoding="utf-8")

    parser = GraphParser()

    with pytest.raises(GraphStructureError, match="root must be a dictionary/object"):
        parser.parse_file(file_path)


def test_should_raise_error_when_nodes_key_is_missing(tmp_path: Path):
    file_path = tmp_path / "graph.json"
    file_path.write_text('{ "edges": [] }', encoding="utf-8")

    parser = GraphParser()

    with pytest.raises(GraphStructureError, match="missing required top-level keys: nodes"):
        parser.parse_file(file_path)


def test_should_raise_error_when_edges_key_is_missing(tmp_path: Path):
    file_path = tmp_path / "graph.json"
    file_path.write_text('{ "nodes": [] }', encoding="utf-8")

    parser = GraphParser()

    with pytest.raises(GraphStructureError, match="missing required top-level keys: edges"):
        parser.parse_file(file_path)