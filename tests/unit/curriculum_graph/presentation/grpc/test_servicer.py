"""Unit tests for the servicer's error handling, correlation and logging (#198)."""
from __future__ import annotations

import json
import logging

import grpc
import pytest

from aigora.curriculum_graph.application.services.published_graph_provider import PublishedGraphProvider
from aigora.curriculum_graph.application.use_cases.read_graph import ReadGraphUseCase
from aigora.curriculum_graph.bootstrap.logging_config import JsonLogFormatter
from aigora.curriculum_graph.presentation.grpc.mappers import PageToken
from aigora.curriculum_graph.presentation.grpc.servicer import (
    REQUEST_ID_TRAILER,
    CurriculumGraphServicer,
    resolve_request_id,
)
from aigora.curriculum_graph.v1 import curriculum_graph_pb2 as pb
from tests.fixtures.curriculum_graph.read_graph import GRAPH_VERSION, StaticGraphReader


class Aborted(Exception):
    pass


class FakeContext:
    def __init__(self) -> None:
        self.trailers: tuple = ()
        self.status: grpc.Status | None = None

    def set_trailing_metadata(self, metadata) -> None:
        self.trailers = tuple(metadata)

    def abort_with_status(self, status: grpc.Status) -> None:
        self.status = status
        raise Aborted()

    @property
    def request_id(self) -> str:
        return dict(self.trailers)[REQUEST_ID_TRAILER]


def _servicer(loaded: bool = True) -> CurriculumGraphServicer:
    provider = PublishedGraphProvider(StaticGraphReader())
    if loaded:
        provider.load()
    return CurriculumGraphServicer(ReadGraphUseCase(provider), provider)


def _detail(ctx: FakeContext) -> pb.ErrorDetail:
    from google.rpc import status_pb2

    status = status_pb2.Status.FromString(dict(ctx.status.trailing_metadata)["grpc-status-details-bin"])
    detail = pb.ErrorDetail()
    status.details[0].Unpack(detail)
    return detail


def test_supplied_request_id_is_echoed_in_trailer() -> None:
    ctx = FakeContext()
    _servicer().GetNode(pb.GetNodeRequest(context=pb.RequestContext(request_id="abc"), node_id="a.counting"), ctx)
    assert ctx.request_id == "abc"


def test_request_id_generated_when_missing() -> None:
    assert len(resolve_request_id(None)) == 32
    assert resolve_request_id(pb.RequestContext(request_id="  ")) != ""
    ctx = FakeContext()
    _servicer().HealthCheck(pb.HealthCheckRequest(), ctx)
    assert len(ctx.request_id) == 32


def test_failure_aborts_with_canonical_detail_and_same_request_id() -> None:
    ctx = FakeContext()
    with pytest.raises(Aborted):
        _servicer().GetPrerequisites(pb.GetPrerequisitesRequest(node_id="z.none"), ctx)
    assert ctx.status.code == grpc.StatusCode.NOT_FOUND
    detail = _detail(ctx)
    assert detail.code == "CG_NODE_NOT_FOUND" and detail.request_id == ctx.request_id
    assert detail.graph_version == GRAPH_VERSION


def test_unloaded_graph_is_unavailable_but_health_answers() -> None:
    servicer = _servicer(loaded=False)
    ctx = FakeContext()
    with pytest.raises(Aborted):
        servicer.GetGraphMetadata(pb.GetGraphMetadataRequest(), ctx)
    assert ctx.status.code == grpc.StatusCode.UNAVAILABLE and _detail(ctx).graph_version == ""
    health = servicer.HealthCheck(pb.HealthCheckRequest(), FakeContext())
    assert health.status == pb.HealthCheckResponse.SERVING_STATUS_NOT_SERVING


def test_version_mismatch_does_not_echo_a_version() -> None:
    ctx = FakeContext()
    with pytest.raises(Aborted):
        _servicer().GetNode(
            pb.GetNodeRequest(context=pb.RequestContext(graph_version="1999.1"), node_id="a.counting"), ctx
        )
    assert ctx.status.code == grpc.StatusCode.FAILED_PRECONDITION
    assert _detail(ctx).code == "CG_INVALID_GRAPH_VERSION" and _detail(ctx).graph_version == ""


def test_page_token_from_another_version_is_invalid_request() -> None:
    token = PageToken(graph_version="older", domain="", profile_id="", offset=2).encode()
    ctx = FakeContext()
    with pytest.raises(Aborted):
        _servicer().ListNodes(pb.ListNodesRequest(page_token=token), ctx)
    assert ctx.status.code == grpc.StatusCode.INVALID_ARGUMENT
    assert _detail(ctx).graph_version == GRAPH_VERSION


def test_listing_pages_through_all_nodes() -> None:
    servicer, ids, token = _servicer(), [], ""
    while True:
        response = servicer.ListNodes(pb.ListNodesRequest(page_size=4, page_token=token), FakeContext())
        ids += [n.id for n in response.nodes]
        token = response.next_page_token
        if not token:
            break
    assert ids == sorted(ids) and len(ids) == 6


def test_unexpected_exception_is_internal(monkeypatch: pytest.MonkeyPatch) -> None:
    servicer = _servicer()
    monkeypatch.setattr(servicer._use_case, "execute", lambda *_: (_ for _ in ()).throw(RuntimeError("secret")))
    ctx = FakeContext()
    with pytest.raises(Aborted):
        servicer.GetNode(pb.GetNodeRequest(node_id="a.counting"), ctx)
    assert ctx.status.code == grpc.StatusCode.INTERNAL and "secret" not in ctx.status.details


def test_each_call_logs_one_structured_event(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO, logger="aigora.curriculum_graph.grpc")
    servicer = _servicer()
    servicer.GetNode(pb.GetNodeRequest(context=pb.RequestContext(request_id="ok-1"), node_id="a.counting"), FakeContext())
    with pytest.raises(Aborted):
        servicer.GetNode(pb.GetNodeRequest(context=pb.RequestContext(request_id="ko-1"), node_id="z"), FakeContext())
    events = [json.loads(JsonLogFormatter().format(r)) for r in caplog.records if r.getMessage() == "grpc_request"]
    assert [(e["request_id"], e["grpc_status"], e["error_code"], e["level"]) for e in events] == [
        ("ok-1", "OK", "", "INFO"),
        ("ko-1", "NOT_FOUND", "CG_NODE_NOT_FOUND", "WARNING"),
    ]
    assert all(e["rpc_method"] == "GetNode" and e["graph_version"] == GRAPH_VERSION for e in events)
    assert all(isinstance(e["latency_ms"], float) for e in events)
