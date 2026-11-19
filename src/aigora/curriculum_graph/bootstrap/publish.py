"""Composition root and CLI for publishing a Curriculum Graph to Neo4j.

Usage:
    python -m aigora.curriculum_graph.bootstrap.publish --input data/graph/canonical/graph.json
    python -m aigora.curriculum_graph.bootstrap.publish --input graph.yaml --export-format csv --export-dir out/

Environment: NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE (default neo4j).
"""
from __future__ import annotations

import argparse
import logging
import sys

from aigora.curriculum_graph.application.use_cases.load_graph import LoadGraphUseCase
from aigora.curriculum_graph.application.use_cases.publish_graph import PublishGraphCommand, PublishGraphUseCase
from aigora.curriculum_graph.bootstrap.logging_config import configure_logging

logger = logging.getLogger("aigora.curriculum_graph.publish")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="publish", description="Publish a Curriculum Graph to Neo4j.")
    parser.add_argument("--input", required=True, metavar="FILE", help="Canonical graph file (YAML or JSON).")
    parser.add_argument("--export-format", choices=["csv", "json", "yaml"], default=None,
                        help="Also export the loaded graph in this format.")
    parser.add_argument("--export-dir", metavar="DIR", default=None, help="Output directory for --export-format.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.export_format and not args.export_dir:
        build_parser().error("--export-dir is required with --export-format.")

    from aigora.curriculum_graph.infrastructure.files.exporters.curriculum_graph_exporter_registry_factory import (
        build_file_curriculum_graph_exporter_registry,
    )
    from aigora.curriculum_graph.infrastructure.files.pipelines.curriculum_graph_loading_pipeline_factory import (
        build_file_curriculum_graph_loading_pipeline,
    )
    from aigora.curriculum_graph.infrastructure.neo4j import Neo4jClient, Neo4jCurriculumGraphRepository

    configure_logging()
    with Neo4jClient() as client:
        use_case = PublishGraphUseCase(
            loader=LoadGraphUseCase(build_file_curriculum_graph_loading_pipeline()),
            repository=Neo4jCurriculumGraphRepository(client),
            exporter_registry=build_file_curriculum_graph_exporter_registry(),
        )
        result = use_case.execute(
            PublishGraphCommand(
                file_path=args.input,
                export_graph=bool(args.export_format),
                export_output_dir=args.export_dir,
                export_format=args.export_format or "csv",
            )
        )
    logger.info(
        "graph_published",
        extra={
            "graph_version": result.graph_version,
            "nodes": result.nodes_published,
            "edges": result.edges_published,
            "profiles": result.profiles_published,
        },
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
