"""Integration tests for the Curriculum Graph gRPC API against a live Neo4j (#199).

The graph is published with the real repository, served through the real
composition root and Neo4j reader, and queried over a real gRPC channel.

The tests replace the active published graph, so run them only against a
disposable Neo4j instance:

    NEO4J_INTEGRATION_TESTS=1 NEO4J_URI=bolt://localhost:7687 \\
    NEO4J_USERNAME=neo4j NEO4J_PASSWORD=... \\
    pytest -m integration tests/integration/curriculum_graph/presentation
"""
from __future__ import annotations

import os
from collections.abc import Iterator

import grpc
import pytest

from aigora.curriculum_graph.bootstrap.grpc_server import RunningServer, start_server
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.infrastructure.neo4j import (
    Neo4jClient,
    Neo4jCurriculumGraphReader,
    Neo4jCurriculumGraphRepository,
)
from aigora.curriculum_graph.presentation.grpc.errors import error_detail_from
from aigora.curriculum_graph.v1 import curriculum_graph_pb2 as pb
from aigora.curriculum_graph.v1 import curriculum_graph_pb2_grpc as pb_grpc
from aigora.shared.config.settings import GrpcServerSettings
from tests.fixtures.curriculum_graph.read_graph import GRAPH_VERSION, make_graph, make_node

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.environ.get("NEO4J_INTEGRATION_TESTS"), reason="NEO4J_INTEGRATION_TESTS not set"),
]

NEXT_VERSION = "2026.12.0"


def _publish(client: Neo4jClient, graph: CurriculumGraph) -> None:
    repository = Neo4jCurriculumGraphRepository(client=client)
    repository.apply_schema()
    repository.persist(graph)
    repository.validate(graph)


@pytest.fixture(scope="module")
def client() -> Iterator[Neo4jClient]:
    neo4j = Neo4jClient()
    _publish(neo4j, make_graph())
    yield neo4j
    neo4j.close()


@pytest.fixture(scope="module")
def server(client: Neo4jClient) -> Iterator[RunningServer]:
    running = start_server(Neo4jCurriculumGraphReader(client), GrpcServerSettings(port=0), host="127.0.0.1")
    yield running
    running.stop(grace=None)


@pytest.fixture(scope="module")
def stub(server: RunningServer) -> Iterator[pb_grpc.CurriculumGraphServiceStub]:
    channel = grpc.insecure_channel(f"127.0.0.1:{server.port}")
    yield pb_grpc.CurriculumGraphServiceStub(channel)
    channel.close()


def _fail(call, request) -> tuple[grpc.StatusCode, pb.ErrorDetail]:
    with pytest.raises(grpc.RpcError) as exc:
        call(request)
    detail = error_detail_from(exc.value)
    assert detail is not None, "every failure must carry an ErrorDetail"
    return exc.value.code(), detail


# ---------------------------------------------------------------------------
# Health and successful flows
# ---------------------------------------------------------------------------

def test_health_check_reports_serving_published_version(stub) -> None:
    response = stub.HealthCheck(pb.HealthCheckRequest())
    assert response.status == pb.HealthCheckResponse.SERVING_STATUS_SERVING
    assert response.graph_version == GRAPH_VERSION


def test_metadata_matches_published_graph(stub) -> None:
    response = stub.GetGraphMetadata(pb.GetGraphMetadataRequest())
    assert response.graph_version == GRAPH_VERSION
    assert (response.node_count, response.edge_count, response.profile_count) == (6, 5, 1)
    assert list(response.domains) == ["algebra", "arithmetic", "geometry"]


def test_get_node_returns_lossless_concept(stub) -> None:
    node = stub.GetNode(pb.GetNodeRequest(node_id="b.quadratics")).node
    assert node.name == "Quadratics" and node.description == "b.quadratics description"
    assert [c.level for c in node.mastery_criteria] == [pb.MASTERY_LEVEL_RECOGNISES, pb.MASTERY_LEVEL_INDEPENDENT]
    assert list(node.error_taxonomy) == ["b.quadratics.misconception"]
    assert list(node.regression_ids) == ["b.linear-equations"]


def test_list_nodes_pages_deterministically(stub) -> None:
    ids, token, pages = [], "", 0
    while True:
        response = stub.ListNodes(pb.ListNodesRequest(page_size=2, page_token=token))
        assert response.graph_version == GRAPH_VERSION and response.total_size == 6
        ids += [n.id for n in response.nodes]
        token, pages = response.next_page_token, pages + 1
        if not token:
            break
    assert pages == 3 and ids == sorted(ids) and len(set(ids)) == 6


def test_list_nodes_by_profile(stub) -> None:
    response = stub.ListNodes(pb.ListNodesRequest(profile_id="profile.core"))
    assert [n.id for n in response.nodes] == ["a.counting", "a.fractions", "b.linear-equations"]


def test_prerequisites_keep_hard_and_soft_kinds(stub) -> None:
    response = stub.GetPrerequisites(pb.GetPrerequisitesRequest(node_id="b.linear-equations"))
    assert [(p.node.id, p.kind) for p in response.prerequisites] == [
        ("a.fractions", pb.PREREQUISITE_KIND_HARD),
        ("a.decimals", pb.PREREQUISITE_KIND_SOFT),
    ]
    hard_only = stub.GetPrerequisites(pb.GetPrerequisitesRequest(node_id="b.linear-equations", include_soft=False))
    assert [p.node.id for p in hard_only.prerequisites] == ["a.fractions"]


def test_regression_targets_survive_publication(stub) -> None:
    response = stub.GetRegressionTargets(pb.GetRegressionTargetsRequest(node_id="b.quadratics"))
    assert [n.id for n in response.targets] == ["b.linear-equations", "a.fractions"]


def test_learning_path_found_and_unreachable(stub) -> None:
    found = stub.GetLearningPath(pb.GetLearningPathRequest(start_node_id="a.counting", target_node_id="b.quadratics"))
    assert found.path_found and [n.id for n in found.path] == [
        "a.counting", "a.fractions", "b.linear-equations", "b.quadratics",
    ]
    unreachable = stub.GetLearningPath(
        pb.GetLearningPathRequest(start_node_id="a.counting", target_node_id="b.quadratics", include_soft=False)
    )
    assert not unreachable.path_found and len(unreachable.path) == 0
    assert unreachable.graph_version == GRAPH_VERSION


def test_request_id_round_trips_in_trailer(stub) -> None:
    _, call = stub.GetNode.with_call(
        pb.GetNodeRequest(context=pb.RequestContext(request_id="it-42"), node_id="a.counting")
    )
    assert dict(call.trailing_metadata())["x-request-id"] == "it-42"


# ---------------------------------------------------------------------------
# Failing flows
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "rpc,request_,status,code,versioned",
    [
        ("GetNode", pb.GetNodeRequest(node_id="z.unknown"), grpc.StatusCode.NOT_FOUND, "CG_NODE_NOT_FOUND", True),
        ("GetPrerequisites", pb.GetPrerequisitesRequest(node_id="z.unknown"), grpc.StatusCode.NOT_FOUND,
         "CG_NODE_NOT_FOUND", True),
        ("GetRegressionTargets", pb.GetRegressionTargetsRequest(node_id="z.unknown"), grpc.StatusCode.NOT_FOUND,
         "CG_NODE_NOT_FOUND", True),
        ("GetLearningPath", pb.GetLearningPathRequest(start_node_id="a.counting", target_node_id="z.unknown"),
         grpc.StatusCode.NOT_FOUND, "CG_NODE_NOT_FOUND", True),
        ("ListNodes", pb.ListNodesRequest(profile_id="profile.unknown"), grpc.StatusCode.NOT_FOUND,
         "CG_PROFILE_NOT_FOUND", True),
        ("GetNode", pb.GetNodeRequest(node_id=""), grpc.StatusCode.INVALID_ARGUMENT, "CG_INVALID_REQUEST", True),
        ("ListNodes", pb.ListNodesRequest(page_size=-5), grpc.StatusCode.INVALID_ARGUMENT, "CG_INVALID_REQUEST",
         False),
        ("ListNodes", pb.ListNodesRequest(page_token="%%%"), grpc.StatusCode.INVALID_ARGUMENT,
         "CG_INVALID_REQUEST", False),
        ("GetNode", pb.GetNodeRequest(context=pb.RequestContext(graph_version="1999.01.0"), node_id="a.counting"),
         grpc.StatusCode.FAILED_PRECONDITION, "CG_INVALID_GRAPH_VERSION", False),
    ],
)
def test_failures_map_to_canonical_errors(stub, rpc, request_, status, code, versioned) -> None:
    actual_status, detail = _fail(getattr(stub, rpc), request_)
    assert (actual_status, detail.code) == (status, code)
    assert detail.request_id
    assert detail.graph_version == (GRAPH_VERSION if versioned else "")


def test_unreachable_store_is_unavailable_and_not_serving() -> None:
    dead = Neo4jClient(uri="bolt://127.0.0.1:1", username="neo4j", password="x")
    running = start_server(
        Neo4jCurriculumGraphReader(dead), GrpcServerSettings(port=0, load_retry_seconds=60), host="127.0.0.1"
    )
    channel = grpc.insecure_channel(f"127.0.0.1:{running.port}")
    try:
        stub = pb_grpc.CurriculumGraphServiceStub(channel)
        health = stub.HealthCheck(pb.HealthCheckRequest())
        assert health.status == pb.HealthCheckResponse.SERVING_STATUS_NOT_SERVING
        status, detail = _fail(stub.GetGraphMetadata, pb.GetGraphMetadataRequest())
        assert (status, detail.code, detail.graph_version) == (grpc.StatusCode.UNAVAILABLE, "CG_GRAPH_UNAVAILABLE", "")
        assert "127.0.0.1" not in detail.message
    finally:
        channel.close()
        running.stop(grace=None)
        dead.close()


def test_republication_serves_only_the_new_version(client: Neo4jClient) -> None:
    """Concepts left over from the previous version are not served after republishing."""
    graph = CurriculumGraph(version=NEXT_VERSION)
    graph.add_node(make_node("a.counting", "arithmetic"))
    graph.add_node(make_node("d.statistics", "statistics"))
    _publish(client, graph)
    try:
        running = start_server(Neo4jCurriculumGraphReader(client), GrpcServerSettings(port=0), host="127.0.0.1")
        channel = grpc.insecure_channel(f"127.0.0.1:{running.port}")
        try:
            stub = pb_grpc.CurriculumGraphServiceStub(channel)
            metadata = stub.GetGraphMetadata(pb.GetGraphMetadataRequest())
            assert (metadata.graph_version, metadata.node_count, metadata.edge_count) == (NEXT_VERSION, 2, 0)
            assert [n.id for n in stub.ListNodes(pb.ListNodesRequest()).nodes] == ["a.counting", "d.statistics"]
        finally:
            channel.close()
            running.stop(grace=None)
    finally:
        _publish(client, make_graph())  # restore the module's baseline for test-order independence
