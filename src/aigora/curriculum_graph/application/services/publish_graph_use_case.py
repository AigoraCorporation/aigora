from __future__ import annotations

from aigora.curriculum_graph.application.services.graph_publication_service import GraphPublicationService
from aigora.curriculum_graph.application.use_cases.publish_graph.publish_graph_command import PublishGraphCommand


class PublishGraphUseCase:
    """Application use case responsible for publishing a Curriculum Graph."""

    def __init__(self, publication_service: GraphPublicationService) -> None:
        self._publication_service = publication_service

    def execute(self, command: PublishGraphCommand) -> None:
        self._publication_service.publish(file_path=command.file_path, export_csv=command.export_csv, csv_output_dir=command.csv_output_dir)
