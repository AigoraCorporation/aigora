"""In-process smoke test: every RPC served through the real composition root (ADR-007)."""
from __future__ import annotations

from collections.abc import Iterator

import grpc
import pytest

from aigora.curriculum_graph.bootstrap.grpc_server import RunningServer, start_server
from aigora.curriculum_graph.v1 import curriculum_graph_pb2 as pb
from aigora.curriculum_graph.v1 import curriculum_graph_pb2_grpc as pb_grpc
from aigora.shared.config.settings import GrpcServerSettings
from tests.fixtures.curriculum_graph.read_graph import GRAPH_VERSION, StaticGraphReader


@pytest.fixture
def stub() -> Iterator[pb_grpc.CurriculumGraphServiceStub]:
    running: RunningServer = start_server(
        StaticGraphReader(), GrpcServerSettings(port=0), host="127.0.0.1"
    )
    channel = grpc.insecure_channel(f"127.0.0.1:{running.port}")
    try:
        yield pb_grpc.CurriculumGraphServiceStub(channel)
    finally:
        channel.close()
        running.stop(grace=None)


def test_all_rpcs_answer_with_graph_version(stub: pb_grpc.CurriculumGraphServiceStub) -> None:
    health = stub.HealthCheck(pb.HealthCheckRequest())
    assert health.status == pb.HealthCheckResponse.SERVING_STATUS_SERVING
    assert health.graph_version == GRAPH_VERSION

    assert stub.GetGraphMetadata(pb.GetGraphMetadataRequest()).node_count == 6
    node = stub.GetNode(pb.GetNodeRequest(node_id="a.fractions"))
    assert node.graph_version == GRAPH_VERSION and node.node.domain == "arithmetic"
    assert [n.id for n in stub.ListNodes(pb.ListNodesRequest(domain="algebra")).nodes] == [
        "b.linear-equations",
        "b.quadratics",
    ]
    prereqs = stub.GetPrerequisites(pb.GetPrerequisitesRequest(node_id="b.linear-equations"))
    assert [(p.node.id, p.kind) for p in prereqs.prerequisites] == [
        ("a.fractions", pb.PREREQUISITE_KIND_HARD),
        ("a.decimals", pb.PREREQUISITE_KIND_SOFT),
    ]
    targets = stub.GetRegressionTargets(pb.GetRegressionTargetsRequest(node_id="b.quadratics"))
    assert [n.id for n in targets.targets] == ["b.linear-equations", "a.fractions"]
    path = stub.GetLearningPath(pb.GetLearningPathRequest(start_node_id="a.counting", target_node_id="b.quadratics"))
    assert path.path_found and len(path.path) == 4


def test_unknown_node_maps_to_not_found(stub: pb_grpc.CurriculumGraphServiceStub) -> None:
    with pytest.raises(grpc.RpcError) as exc:
        stub.GetNode(pb.GetNodeRequest(node_id="z.unknown"))
    assert exc.value.code() == grpc.StatusCode.NOT_FOUND
