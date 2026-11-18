"""Translation of application read errors into gRPC statuses (ADR-007)."""
from __future__ import annotations

import grpc

from aigora.curriculum_graph.application.errors.read_graph_errors import (
    GraphNodeNotFoundError,
    GraphProfileNotFoundError,
    GraphUnavailableError,
    GraphVersionMismatchError,
    InvalidReadRequestError,
    ReadGraphError,
)

STATUS_BY_ERROR: dict[type[ReadGraphError], grpc.StatusCode] = {
    GraphNodeNotFoundError: grpc.StatusCode.NOT_FOUND,
    GraphProfileNotFoundError: grpc.StatusCode.NOT_FOUND,
    GraphVersionMismatchError: grpc.StatusCode.FAILED_PRECONDITION,
    GraphUnavailableError: grpc.StatusCode.UNAVAILABLE,
    InvalidReadRequestError: grpc.StatusCode.INVALID_ARGUMENT,
}


def status_for(error: ReadGraphError) -> grpc.StatusCode:
    return STATUS_BY_ERROR.get(type(error), grpc.StatusCode.INTERNAL)


def abort_with(context: grpc.ServicerContext, error: ReadGraphError) -> None:
    """Abort the RPC with the status mapped from `error`. Never returns."""
    context.abort(status_for(error), error.message)
