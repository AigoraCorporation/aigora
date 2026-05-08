from __future__ import annotations

from pathlib import Path

from aigora.curriculum_graph.infrastructure.files.csv.graph_csv_exporter import GraphCsvExporter
from aigora.curriculum_graph.application.use_cases.load_graph.load_graph_use_case import LoadGraphUseCase
from aigora.curriculum_graph.domain.repositories.graph_repository import GraphRepository


class GraphPublicationService:
    """Orchestrates the full Curriculum Graph publication pipeline.

    Pipeline (in order):
    1. Load the graph from a file using LoadGraphUseCase
    2. Optionally export canonical CSVs using GraphCsvExporter
    3. Apply the database schema using GraphRepository.apply_schema()
    4. Persist the graph using GraphRepository.persist()
    5. Validate the persisted graph using GraphRepository.validate()
    """

    def __init__(
        self,
        loader: LoadGraphUseCase,
        repository: GraphRepository,
        exporter: GraphCsvExporter | None = None,
    ) -> None:
        self._loader = loader
        self._repository = repository
        self._exporter = exporter

    def publish(
        self,
        file_path: str | Path,
        export_csv: bool = False,
        csv_output_dir: str | Path | None = None,
    ) -> None:
        """Run the full publication pipeline for the given graph file.

        Args:
            file_path: Path to the canonical graph YAML/JSON file.
            export_csv: If True, export canonical CSVs before persisting.
            csv_output_dir: Directory to write CSV files to when export_csv
                is True. Required when export_csv is True and no exporter
                output directory is implied by context.

        Raises:
            LoadGraphUseCaseError: If the graph file cannot be loaded or is invalid.
            GraphCsvExporterError: If CSV export fails.
            GraphPersistenceValidationError: If post-persistence validation fails.
        """
        graph = self._loader.load(file_path)

        if export_csv:
            if self._exporter is None:
                raise ValueError(
                    "export_csv=True requires an exporter to be provided at construction time."
                )
            if csv_output_dir is None:
                raise ValueError(
                    "csv_output_dir must be provided when export_csv=True."
                )
            self._exporter.export(graph, csv_output_dir)

        self._repository.apply_schema()
        self._repository.persist(graph)
        self._repository.validate(graph)
