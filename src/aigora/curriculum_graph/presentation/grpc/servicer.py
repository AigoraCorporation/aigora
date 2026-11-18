"""gRPC servicer for aigora.curriculum_graph.v1.CurriculumGraphService (ADR-007).

Handlers only translate: request -> application command, application result
-> response, failure -> canonical rich status. They never touch
infrastructure. Every call is logged once as a structured `grpc_request`
event and returns its correlation id in the `x-request-id` trailer.
"""
from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Callable
from typing import TypeVar

import grpc

from aigora.curriculum_graph.application.errors.read_graph_errors import InvalidReadRequestError
from aigora.curriculum_graph.application.services.published_graph_provider import PublishedGraphProvider
from aigora.curriculum_graph.application.use_cases.read_graph import ReadGraphUseCase
from aigora.curriculum_graph.v1 import curriculum_graph_pb2 as pb
from aigora.curriculum_graph.v1 import curriculum_graph_pb2_grpc as pb_grpc

from . import mappers
from .errors import map_error

T = TypeVar("T")

REQUEST_ID_TRAILER = "x-request-id"
logger = logging.getLogger("aigora.curriculum_graph.grpc")


def resolve_request_id(context: pb.RequestContext | None) -> str:
    supplied = context.request_id.strip() if context is not None else ""
    return supplied or uuid.uuid4().hex


class CurriculumGraphServicer(pb_grpc.CurriculumGraphServiceServicer):
    def __init__(self, use_case: ReadGraphUseCase, provider: PublishedGraphProvider) -> None:
        self._use_case = use_case
        self._provider = provider

    # ------------------------------------------------------------------
    # RPCs
    # ------------------------------------------------------------------

    def GetGraphMetadata(self, request: pb.GetGraphMetadataRequest, context: grpc.ServicerContext):
        return self._handle(
            "GetGraphMetadata",
            request.context,
            context,
            lambda: mappers.to_get_graph_metadata_response(
                self._use_case.execute(mappers.to_get_graph_metadata_command(request))
            ),
        )

    def GetNode(self, request: pb.GetNodeRequest, context: grpc.ServicerContext):
        return self._handle(
            "GetNode",
            request.context,
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

        return self._handle("ListNodes", request.context, context, run)

    def GetPrerequisites(self, request: pb.GetPrerequisitesRequest, context: grpc.ServicerContext):
        return self._handle(
            "GetPrerequisites",
            request.context,
            context,
            lambda: mappers.to_get_prerequisites_response(
                self._use_case.execute(mappers.to_get_prerequisites_command(request))
            ),
        )

    def GetRegressionTargets(self, request: pb.GetRegressionTargetsRequest, context: grpc.ServicerContext):
        return self._handle(
            "GetRegressionTargets",
            request.context,
            context,
            lambda: mappers.to_get_regression_targets_response(
                self._use_case.execute(mappers.to_get_regression_targets_command(request))
            ),
        )

    def GetLearningPath(self, request: pb.GetLearningPathRequest, context: grpc.ServicerContext):
        return self._handle(
            "GetLearningPath",
            request.context,
            context,
            lambda: mappers.to_get_learning_path_response(
                self._use_case.execute(mappers.to_get_learning_path_command(request))
            ),
        )

    def HealthCheck(self, request: pb.HealthCheckRequest, context: grpc.ServicerContext):
        return self._handle(
            "HealthCheck",
            None,
            context,
            lambda: mappers.to_health_check_response(self._provider.is_ready, self._provider.graph_version),
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _handle(
        self,
        method: str,
        request_context: pb.RequestContext | None,
        context: grpc.ServicerContext,
        call: Callable[[], T],
    ) -> T:
        request_id = resolve_request_id(request_context)
        context.set_trailing_metadata(((REQUEST_ID_TRAILER, request_id),))
        started = time.perf_counter()
        try:
            response = call()
        except Exception as error:  # noqa: BLE001 - every failure must map to the canonical model
            mapped = map_error(error, request_id)
            _log(method, request_id, started, mapped.status, mapped.detail.code, mapped.detail.graph_version, error)
            context.abort_with_status(mapped.to_rpc_status())
            raise  # unreachable: abort_with_status raises
        _log(method, request_id, started, grpc.StatusCode.OK, "", getattr(response, "graph_version", ""), None)
        return response


def _log(
    method: str,
    request_id: str,
    started: float,
    status: grpc.StatusCode,
    code: str,
    graph_version: str,
    error: Exception | None,
) -> None:
    fields = {
        "rpc_method": method,
        "request_id": request_id,
        "grpc_status": status.name,
        "error_code": code,
        "graph_version": graph_version,
        "latency_ms": round((time.perf_counter() - started) * 1000, 3),
    }
    if status is grpc.StatusCode.INTERNAL:
        logger.error("grpc_request", extra=fields, exc_info=error)
    elif status is grpc.StatusCode.OK:
        logger.info("grpc_request", extra=fields)
    else:
        logger.warning("grpc_request", extra=fields)


def register(server: grpc.Server, servicer: CurriculumGraphServicer) -> None:
    """Register the servicer on a gRPC server (keeps generated code inside presentation)."""
    pb_grpc.add_CurriculumGraphServiceServicer_to_server(servicer, server)
