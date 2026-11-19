"""Unit tests for the canonical gRPC error mapping (#198, ADR-007 RQ-3/RQ-4)."""
from __future__ import annotations

import grpc
import pytest
from google.rpc import status_pb2

from aigora.curriculum_graph.application.errors.read_graph_errors import (
    GraphNodeNotFoundError,
    GraphProfileNotFoundError,
    GraphUnavailableError,
    GraphVersionMismatchError,
    InvalidReadRequestError,
    ReadGraphError,
)
from aigora.curriculum_graph.presentation.grpc.errors import (
    ERROR_MAPPINGS,
    INTERNAL_MESSAGE,
    error_detail_from,
    map_error,
)
from aigora.curriculum_graph.v1 import curriculum_graph_pb2 as pb

CASES = [
    (GraphNodeNotFoundError, grpc.StatusCode.NOT_FOUND, "CG_NODE_NOT_FOUND", False),
    (GraphProfileNotFoundError, grpc.StatusCode.NOT_FOUND, "CG_PROFILE_NOT_FOUND", False),
    (GraphVersionMismatchError, grpc.StatusCode.FAILED_PRECONDITION, "CG_INVALID_GRAPH_VERSION", False),
    (GraphUnavailableError, grpc.StatusCode.UNAVAILABLE, "CG_GRAPH_UNAVAILABLE", True),
    (InvalidReadRequestError, grpc.StatusCode.INVALID_ARGUMENT, "CG_INVALID_REQUEST", False),
]


def test_taxonomy_is_closed_and_one_to_one() -> None:
    assert {cls for cls, *_ in CASES} == set(ERROR_MAPPINGS)
    assert len({m.code for m in ERROR_MAPPINGS.values()}) == len(ERROR_MAPPINGS)


@pytest.mark.parametrize("error_cls,status,code,retryable", CASES)
def test_each_error_maps_to_status_code_and_payload(error_cls, status, code, retryable) -> None:
    mapped = map_error(error_cls("safe message", graph_version="2026.11.0"), "req-9")
    assert mapped.status == status
    assert mapped.detail == pb.ErrorDetail(code=code, message="safe message", request_id="req-9", graph_version="2026.11.0")
    assert ERROR_MAPPINGS[error_cls].retryable is retryable
    assert error_cls.code == code


@pytest.mark.parametrize("error_cls", [cls for cls, *_ in CASES])
def test_graph_version_omitted_when_not_bound(error_cls) -> None:
    assert map_error(error_cls("m"), "r").detail.graph_version == ""


@pytest.mark.parametrize("error", [RuntimeError("bolt://db:7687 password=secret"), KeyError("x"), ReadGraphError("base")])
def test_unexpected_errors_become_internal_without_leaking(error: Exception) -> None:
    mapped = map_error(error, "req-1")
    assert mapped.status == grpc.StatusCode.INTERNAL
    assert mapped.detail == pb.ErrorDetail(code="", message=INTERNAL_MESSAGE, request_id="req-1")


def test_rich_status_packs_exactly_one_error_detail() -> None:
    rpc = map_error(GraphNodeNotFoundError("Node not found: 'x'", graph_version="v"), "r").to_rpc_status()
    assert rpc.code == grpc.StatusCode.NOT_FOUND
    assert rpc.details == "Node not found: 'x'"
    (key, value), = rpc.trailing_metadata
    assert key == "grpc-status-details-bin"
    status = status_pb2.Status.FromString(value)
    assert status.code == grpc.StatusCode.NOT_FOUND.value[0] and len(status.details) == 1
    detail = pb.ErrorDetail()
    assert status.details[0].Unpack(detail) and detail.code == "CG_NODE_NOT_FOUND"


class _FakeRpcError(grpc.RpcError, grpc.Call):
    def __init__(self, code: grpc.StatusCode, details: str, trailing=()) -> None:
        self._code, self._details, self._trailing = code, details, trailing

    def code(self): return self._code
    def details(self): return self._details
    def trailing_metadata(self): return self._trailing
    def initial_metadata(self): return ()
    def is_active(self): return False
    def time_remaining(self): return None
    def cancel(self): return False
    def add_callback(self, callback): return False


def test_error_detail_from_round_trip() -> None:
    rpc = map_error(GraphUnavailableError("down"), "r-2").to_rpc_status()
    detail = error_detail_from(_FakeRpcError(rpc.code, rpc.details, rpc.trailing_metadata))
    assert detail is not None and (detail.code, detail.request_id) == ("CG_GRAPH_UNAVAILABLE", "r-2")


def test_error_detail_from_plain_status_is_none() -> None:
    assert error_detail_from(_FakeRpcError(grpc.StatusCode.UNAVAILABLE, "connection refused")) is None
