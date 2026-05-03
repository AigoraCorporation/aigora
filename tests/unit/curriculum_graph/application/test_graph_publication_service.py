from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from aigora.curriculum_graph.application.graph_publication_service import (
    GraphPublicationService,
)


def _make_service(
    loader=None,
    repository=None,
    exporter=None,
):
    loader = loader or MagicMock()
    repository = repository or MagicMock()
    return GraphPublicationService(
        loader=loader,
        repository=repository,
        exporter=exporter,
    )


class TestGraphPublicationServiceUnit:
    def test_publish_calls_pipeline_in_order(self):
        loader = MagicMock()
        repository = MagicMock()
        graph = MagicMock()
        loader.load.return_value = graph

        service = _make_service(loader=loader, repository=repository)
        service.publish("graph.yaml")

        loader.load.assert_called_once_with("graph.yaml")
        repository.apply_schema.assert_called_once()
        repository.persist.assert_called_once_with(graph)
        repository.validate.assert_called_once_with(graph)

    def test_publish_calls_apply_schema_before_persist(self):
        call_order: list[str] = []
        loader = MagicMock()
        repository = MagicMock()
        repository.apply_schema.side_effect = lambda: call_order.append("apply_schema")
        repository.persist.side_effect = lambda g: call_order.append("persist")
        repository.validate.side_effect = lambda g: call_order.append("validate")
        loader.load.return_value = MagicMock()

        service = _make_service(loader=loader, repository=repository)
        service.publish("graph.yaml")

        assert call_order == ["apply_schema", "persist", "validate"]

    def test_publish_without_csv_export_skips_exporter(self):
        exporter = MagicMock()
        service = _make_service(exporter=exporter)
        service.publish("graph.yaml", export_csv=False)

        exporter.export.assert_not_called()

    def test_publish_with_csv_export_calls_exporter(self, tmp_path):
        loader = MagicMock()
        exporter = MagicMock()
        graph = MagicMock()
        loader.load.return_value = graph

        service = _make_service(loader=loader, exporter=exporter)
        service.publish("graph.yaml", export_csv=True, csv_output_dir=tmp_path)

        exporter.export.assert_called_once_with(graph, tmp_path)

    def test_publish_csv_export_before_persist(self, tmp_path):
        call_order: list[str] = []
        loader = MagicMock()
        repository = MagicMock()
        exporter = MagicMock()
        loader.load.return_value = MagicMock()
        exporter.export.side_effect = lambda g, d: call_order.append("export")
        repository.apply_schema.side_effect = lambda: call_order.append("apply_schema")
        repository.persist.side_effect = lambda g: call_order.append("persist")
        repository.validate.side_effect = lambda g: call_order.append("validate")

        service = _make_service(loader=loader, repository=repository, exporter=exporter)
        service.publish("graph.yaml", export_csv=True, csv_output_dir=tmp_path)

        assert call_order == ["export", "apply_schema", "persist", "validate"]

    def test_publish_export_csv_without_exporter_raises(self, tmp_path):
        service = _make_service(exporter=None)
        with pytest.raises(ValueError, match="exporter"):
            service.publish("graph.yaml", export_csv=True, csv_output_dir=tmp_path)

    def test_publish_export_csv_without_output_dir_raises(self):
        exporter = MagicMock()
        service = _make_service(exporter=exporter)
        with pytest.raises(ValueError, match="csv_output_dir"):
            service.publish("graph.yaml", export_csv=True, csv_output_dir=None)

    def test_loader_error_propagates(self):
        loader = MagicMock()
        loader.load.side_effect = RuntimeError("load failed")
        service = _make_service(loader=loader)

        with pytest.raises(RuntimeError, match="load failed"):
            service.publish("bad_graph.yaml")

    def test_persist_error_propagates(self):
        loader = MagicMock()
        repository = MagicMock()
        loader.load.return_value = MagicMock()
        repository.persist.side_effect = RuntimeError("persist failed")

        service = _make_service(loader=loader, repository=repository)
        with pytest.raises(RuntimeError, match="persist failed"):
            service.publish("graph.yaml")

    def test_validate_error_propagates(self):
        loader = MagicMock()
        repository = MagicMock()
        loader.load.return_value = MagicMock()
        repository.validate.side_effect = RuntimeError("validation failed")

        service = _make_service(loader=loader, repository=repository)
        with pytest.raises(RuntimeError, match="validation failed"):
            service.publish("graph.yaml")

    def test_publish_accepts_path_object(self):
        loader = MagicMock()
        repository = MagicMock()
        loader.load.return_value = MagicMock()
        service = _make_service(loader=loader, repository=repository)

        service.publish(Path("graph.yaml"))

        loader.load.assert_called_once_with(Path("graph.yaml"))
