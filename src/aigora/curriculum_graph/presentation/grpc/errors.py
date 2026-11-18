"""Canonical gRPC error model for the Curriculum Graph API (ADR-007, RQ-3/RQ-4).

Every failed RPC is aborted with a rich status: the standard status code plus a
`google.rpc.Status` whose details hold exactly one
`aigora.curriculum_graph.v1.ErrorDetail` (`code`, `message`, `request_id`,
`graph_version`).
"""
from __future__ import annotations

from dataclasses import dataclass

import grpc
from google.protobuf import any_pb2
from google.rpc import status_pb2
from grpc_status import rpc_status

from aigora.curriculum_graph.application.errors.read_graph_errors import (
    GraphNodeNotFoundError,
    GraphProfileNotFoundError,
    GraphUnavailableError,
    GraphVersionMismatchError,
    InvalidReadRequestError,
    ReadGraphError,
)
from aigora.curriculum_graph.v1 import curriculum_graph_pb2 as pb

INTERNAL_MESSAGE = "Internal server error."


@dataclass(frozen=True)
class ErrorMapping:
    status: grpc.StatusCode
    code: str
    retryable: bool


ERROR_MAPPINGS: dict[type[ReadGraphError], ErrorMapping] = {
    GraphNodeNotFoundError: ErrorMapping(grpc.StatusCode.NOT_FOUND, "CG_NODE_NOT_FOUND", False),
    GraphProfileNotFoundError: ErrorMapping(grpc.StatusCode.NOT_FOUND, "CG_PROFILE_NOT_FOUND", False),
    GraphVersionMismatchError: ErrorMapping(
        grpc.StatusCode.FAILED_PRECONDITION, "CG_INVALID_GRAPH_VERSION", False
    ),
    GraphUnavailableError: ErrorMapping(grpc.StatusCode.UNAVAILABLE, "CG_GRAPH_UNAVAILABLE", True),
    InvalidReadRequestError: ErrorMapping(grpc.StatusCode.INVALID_ARGUMENT, "CG_INVALID_REQUEST", False),
}


@dataclass(frozen=True)
class MappedError:
    """A failure ready to be sent: status code plus the canonical payload."""

    status: grpc.StatusCode
    detail: pb.ErrorDetail

    def to_rpc_status(self) -> grpc.Status:
        packed = any_pb2.Any()
        packed.Pack(self.detail)
        return rpc_status.to_status(
            status_pb2.Status(code=self.status.value[0], message=self.detail.message, details=[packed])
        )


def map_error(error: Exception, request_id: str) -> MappedError:
    """Map any exception raised while serving an RPC to the canonical error model.

    Application read errors map one-to-one (ERROR_MAPPINGS). Anything else is a
    defect: it becomes INTERNAL with a generic message and an empty code, so no
    internal detail leaks to clients.
    """
    if isinstance(error, ReadGraphError):
        mapping = ERROR_MAPPINGS.get(type(error))
        if mapping is not None:
            return MappedError(
                status=mapping.status,
                detail=pb.ErrorDetail(
                    code=mapping.code,
                    message=error.message,
                    request_id=request_id,
                    graph_version=error.graph_version or "",
                ),
            )
    return MappedError(
        status=grpc.StatusCode.INTERNAL,
        detail=pb.ErrorDetail(code="", message=INTERNAL_MESSAGE, request_id=request_id),
    )


def error_detail_from(rpc_error: grpc.RpcError) -> pb.ErrorDetail | None:
    """Client-side helper: extract the ErrorDetail from a failed call, if present."""
    status = rpc_status.from_call(rpc_error)
    if status is None:
        return None
    for detail in status.details:
        if detail.Is(pb.ErrorDetail.DESCRIPTOR):
            unpacked = pb.ErrorDetail()
            detail.Unpack(unpacked)
            return unpacked
    return None
