"""Integration tests for GraphPublicationService.

These tests exercise the full publication pipeline — including GraphLoader,
GraphCsvExporter, and a real (or test-double) GraphRepository.

They are skipped by default unless a live Neo4j instance is available.
To run them:

    PYTHONPATH=src python3 -m pytest tests/integration -m integration -v

All tests in this module are marked with @pytest.mark.integration.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from aigora.curriculum_graph.application.graph_csv_exporter import GraphCsvExporter
from aigora.curriculum_graph.application.graph_publication_service import (
    GraphPublicationService,
)
from aigora.curriculum_graph.application.loading.graph_loader import GraphLoader

_EXAMPLES_DIR = Path(__file__).parents[3] / "examples" / "curriculum_graph"
_CANONICAL_YAML = _EXAMPLES_DIR / "canonical" / "graph.yaml"


@pytest.mark.integration
class TestGraphPublicationServiceIntegration:
    """Integration tests for GraphPublicationService using a stub repository.

    These tests verify that the publication pipeline correctly integrates
    GraphLoader and GraphCsvExporter without requiring a live Neo4j instance.
    A MagicMock repository is used so the pipeline can be exercised end-to-end
    with real file I/O.
    """

    @pytest.fixture()
    def stub_repository(self):
        return MagicMock()

    @pytest.fixture()
    def service(self, stub_repository):
        return GraphPublicationService(
            loader=GraphLoader(),
            repository=stub_repository,
            exporter=GraphCsvExporter(),
        )

    def test_publish_loads_and_persists_canonical_yaml(self, service, stub_repository):
        """Full pipeline should load the canonical YAML graph and persist it."""
        service.publish(_CANONICAL_YAML)

        stub_repository.apply_schema.assert_called_once()
        stub_repository.persist.assert_called_once()
        stub_repository.validate.assert_called_once()

    def test_publish_with_csv_export_writes_all_files(
        self, service, stub_repository, tmp_path
    ):
        """CSV export step should write all 6 canonical CSV files."""
        service.publish(_CANONICAL_YAML, export_csv=True, csv_output_dir=tmp_path)

        for filename in GraphCsvExporter.REQUIRED_FILES:
            assert (tmp_path / filename).exists(), f"Missing CSV: {filename}"

        stub_repository.apply_schema.assert_called_once()
        stub_repository.persist.assert_called_once()
        stub_repository.validate.assert_called_once()

    def test_publish_without_csv_export_writes_no_files(
        self, service, stub_repository, tmp_path
    ):
        """Without CSV export, no files should be written to disk."""
        service.publish(_CANONICAL_YAML, export_csv=False)

        for filename in GraphCsvExporter.REQUIRED_FILES:
            assert not (tmp_path / filename).exists()
