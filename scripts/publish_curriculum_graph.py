#!/usr/bin/env python3
"""CLI entrypoint for the Curriculum Graph publication pipeline.

Thin wrapper around ``python -m aigora.curriculum_graph.bootstrap.publish``.

Usage
-----
    python scripts/publish_curriculum_graph.py --input data/graph/canonical/graph.json
    python scripts/publish_curriculum_graph.py --input graph.yaml --export-format csv --export-dir out/

Environment variables:
    NEO4J_URI       — Bolt URI  (e.g. bolt://localhost:7687)
    NEO4J_USERNAME  — Database username
    NEO4J_PASSWORD  — Database password
    NEO4J_DATABASE  — Target database (default: neo4j)
"""
from __future__ import annotations

import sys

from aigora.curriculum_graph.bootstrap.publish import main

if __name__ == "__main__":
    sys.exit(main())
