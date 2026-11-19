"""Container health probe: exits 0 only when the API reports SERVING.

Usage: python -m aigora.curriculum_graph.presentation.grpc.healthcheck [--target host:port] [--timeout seconds]
"""
from __future__ import annotations

import argparse
import os
import sys

import grpc

from aigora.curriculum_graph.v1 import curriculum_graph_pb2 as pb
from aigora.curriculum_graph.v1 import curriculum_graph_pb2_grpc as pb_grpc


def probe(target: str, timeout: float) -> bool:
    with grpc.insecure_channel(target) as channel:
        try:
            response = pb_grpc.CurriculumGraphServiceStub(channel).HealthCheck(pb.HealthCheckRequest(), timeout=timeout)
        except grpc.RpcError:
            return False
    return response.status == pb.HealthCheckResponse.SERVING_STATUS_SERVING


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=f"127.0.0.1:{os.environ.get('GRPC_PORT', '50051')}")
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args(argv)
    return 0 if probe(args.target, args.timeout) else 1


if __name__ == "__main__":
    sys.exit(main())
