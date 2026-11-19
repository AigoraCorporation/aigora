"""gRPC servicer for aigora.curriculum_graph.v1.CurriculumGraphService (ADR-007).

Handlers only translate: request -> application command, application result
-> response, application error -> gRPC status. They never touch
infrastructure.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

import grpc

from aigora.curriculum_graph.application.errors.read_graph_errors import (
    InvalidReadRequestError,
    ReadGraphError,
)
from aigora.curriculum_graph.application.services.published_graph_provider import PublishedGraphProvider
from aigora.curriculum_graph.application.use_cases.read_graph import ReadGraphUseCase
from aigora.curriculum_graph.v1 import curriculum_graph_pb2 as pb
from aigora.curriculum_graph.v1 import curriculum_graph_pb2_grpc as pb_grpc

from . import mappers
from .errors import abort_with

T = TypeVar("T")


class CurriculumGraphServicer(pb_grpc.CurriculumGraphServiceServicer):
    def __init__(self, use_case: ReadGraphUseCase, provider: PublishedGraphProvider) -> None:
        self._use_case = use_case
        self._provider = provider

    # ------------------------------------------------------------------
    # RPCs
    # ------------------------------------------------------------------

    def GetGraphMetadata(self, request: pb.GetGraphMetadataRequest, context: grpc.ServicerContext):
        return self._handle(
            context,
            lambda: mappers.to_get_graph_metadata_response(
                self._use_case.execute(mappers.to_get_graph_metadata_command(request))
            ),
        )

    def GetNode(self, request: pb.GetNodeRequest, context: grpc.ServicerContext):
        return self._handle(
            context,
            lambda: mappers.to_get_node_response(self._use_case.execute(mappers.to_get_node_command(request))),
        )

    def ListNodes(self, request: pb.ListNodesRequest, context: grpc.ServicerContext):
        def run() -> pb.ListNodesResponse:
            command, token = mappers.to_list_nodes_command(request)
            result = self._use_case.execute(command)
            if token is not None and token.graph_version != result.graph_version:
                raise InvalidReadRequestError(
                    "page_token was issued for another graph version.", graph_version=result.graph_version
                )
            return mappers.to_list_nodes_response(result, command)

        return self._handle(context, run)

    def GetPrerequisites(self, request: pb.GetPrerequisitesRequest, context: grpc.ServicerContext):
        return self._handle(
            context,
            lambda: mappers.to_get_prerequisites_response(
                self._use_case.execute(mappers.to_get_prerequisites_command(request))
            ),
        )

    def GetRegressionTargets(self, request: pb.GetRegressionTargetsRequest, context: grpc.ServicerContext):
        return self._handle(
            context,
            lambda: mappers.to_get_regression_targets_response(
                self._use_case.execute(mappers.to_get_regression_targets_command(request))
            ),
        )

    def GetLearningPath(self, request: pb.GetLearningPathRequest, context: grpc.ServicerContext):
        return self._handle(
            context,
            lambda: mappers.to_get_learning_path_response(
                self._use_case.execute(mappers.to_get_learning_path_command(request))
            ),
        )

    def HealthCheck(self, request: pb.HealthCheckRequest, context: grpc.ServicerContext):
        return mappers.to_health_check_response(self._provider.is_ready, self._provider.graph_version)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _handle(context: grpc.ServicerContext, call: Callable[[], T]) -> T:
        try:
            return call()
        except ReadGraphError as error:
            abort_with(context, error)
            raise  # unreachable: context.abort raises


def register(server: grpc.Server, servicer: CurriculumGraphServicer) -> None:
    """Register the servicer on a gRPC server (keeps generated code inside presentation)."""
    pb_grpc.add_CurriculumGraphServiceServicer_to_server(servicer, server)
