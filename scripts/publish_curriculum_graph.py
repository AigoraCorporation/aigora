#!/usr/bin/env python3
"""CLI entrypoint for the Curriculum Graph publication pipeline.

Usage
-----
    python scripts/publish_curriculum_graph.py --input data/graph/canonical/graph.yaml
    python scripts/publish_curriculum_graph.py --input data/graph/canonical/graph.yaml \\
        --export-csv --csv-output-dir path/to/csv/

Environment variables required (see docker/neo4j/.env.example):
    NEO4J_URI       — Bolt URI  (e.g. bolt://localhost:7687)
    NEO4J_USERNAME  — Database username
    NEO4J_PASSWORD  — Database password
    NEO4J_DATABASE  — Target database (default: neo4j)
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="publish_curriculum_graph",
        description="Publish a Curriculum Graph to Neo4j.",
    )
    parser.add_argument(
        "--input",
        required=True,
        metavar="FILE",
        help="Path to the canonical graph YAML or JSON file.",
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        default=False,
        help="Export canonical CSVs before persisting (default: disabled).",
    )
    parser.add_argument(
        "--csv-output-dir",
        metavar="DIR",
        default=None,
        help="Directory to write CSV files to. Required when --export-csv is set.",
    )
    return parser


def main() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    export_csv: bool = args.export_csv
    csv_output_dir = Path(args.csv_output_dir) if args.csv_output_dir else None

    if export_csv and csv_output_dir is None:
        parser.error("--csv-output-dir is required when --export-csv is set.")

    # Lazy imports so the script can be imported without requiring Neo4j installed
    from aigora.curriculum_graph.application.graph_csv_exporter import GraphCsvExporter
    from aigora.curriculum_graph.application.graph_publication_service import (
        GraphPublicationService,
    )
    from aigora.curriculum_graph.application.loading.graph_loader import GraphLoader
    from aigora.curriculum_graph.infrastructure.neo4j.neo4j_client import Neo4jClient
    from aigora.curriculum_graph.infrastructure.neo4j.neo4j_graph_repository import (
        Neo4jGraphRepository,
    )

    logger.info("Initialising Neo4j client")
    client = Neo4jClient()

    logger.info("Initialising repository and publication service")
    repository = Neo4jGraphRepository(client=client)
    exporter = GraphCsvExporter() if export_csv else None

    service = GraphPublicationService(
        loader=GraphLoader(),
        repository=repository,
        exporter=exporter,
    )

    logger.info("Starting publication pipeline for: %s", input_path)
    if export_csv:
        logger.info("CSV export enabled — output directory: %s", csv_output_dir)

    try:
        service.publish(input_path, export_csv=export_csv, csv_output_dir=csv_output_dir)
    except Exception as exc:
        logger.error("Publication failed: %s", exc)
        sys.exit(1)

    logger.info("Publication completed successfully")


if __name__ == "__main__":
    main()
