"""Unit tests for gRPC request/response mappers (#198)."""
from __future__ import annotations

import pytest

from aigora.curriculum_graph.application.errors.read_graph_errors import InvalidReadRequestError
from aigora.curriculum_graph.application.services.published_graph_provider import PublishedGraphProvider
from aigora.curriculum_graph.application.use_cases.read_graph import (
    GetGraphMetadataCommand,
    GetLearningPathCommand,
    GetNodeCommand,
    GetPrerequisitesCommand,
    GetRegressionTargetsCommand,
    ListNodesCommand,
    MasteryCriterionView,
    NodeView,
    ReadGraphUseCase,
)
from aigora.curriculum_graph.presentation.grpc import mappers
from aigora.curriculum_graph.presentation.grpc.mappers import PageToken
from aigora.curriculum_graph.v1 import curriculum_graph_pb2 as pb
from tests.fixtures.curriculum_graph.read_graph import GRAPH_VERSION, StaticGraphReader


@pytest.fixture(scope="module")
def use_case() -> ReadGraphUseCase:
    provider = PublishedGraphProvider(StaticGraphReader())
    provider.load()
    return ReadGraphUseCase(provider)


def _ctx(version: str = "", request_id: str = "") -> pb.RequestContext:
    return pb.RequestContext(graph_version=version, request_id=request_id)


# ---------------------------------------------------------------------------
# Requests -> commands
# ---------------------------------------------------------------------------

class TestRequestMapping:
    @pytest.mark.parametrize("raw,expected", [("", None), ("   ", None), (" 2026.11.0 ", "2026.11.0")])
    def test_expected_version_blank_means_active(self, raw: str, expected: str | None) -> None:
        assert mappers.expected_version(_ctx(raw)) == expected

    def test_missing_context_means_active_version(self) -> None:
        assert mappers.to_get_graph_metadata_command(pb.GetGraphMetadataRequest()) == GetGraphMetadataCommand()

    def test_get_node_strips_id_and_carries_version(self) -> None:
        command = mappers.to_get_node_command(pb.GetNodeRequest(context=_ctx("v1"), node_id="  a.x "))
        assert command == GetNodeCommand(node_id="a.x", expected_version="v1")

    def test_include_soft_defaults_to_true_when_unset(self) -> None:
        assert mappers.to_get_prerequisites_command(pb.GetPrerequisitesRequest(node_id="n")).include_soft is True
        assert mappers.to_get_learning_path_command(pb.GetLearningPathRequest()).include_soft is True

    def test_include_soft_explicit_false_is_respected(self) -> None:
        prereq = mappers.to_get_prerequisites_command(pb.GetPrerequisitesRequest(node_id="n", include_soft=False))
        path = mappers.to_get_learning_path_command(
            pb.GetLearningPathRequest(start_node_id="a", target_node_id="b", include_soft=False)
        )
        assert prereq == GetPrerequisitesCommand(node_id="n", include_soft=False)
        assert path == GetLearningPathCommand(start_node_id="a", target_node_id="b", include_soft=False)

    def test_regression_targets_command(self) -> None:
        command = mappers.to_get_regression_targets_command(pb.GetRegressionTargetsRequest(node_id="n"))
        assert command == GetRegressionTargetsCommand(node_id="n")

    @pytest.mark.parametrize("page_size,limit", [(0, 100), (1, 1), (250, 250), (1000, 1000), (5000, 1000)])
    def test_page_size_defaults_and_caps(self, page_size: int, limit: int) -> None:
        command, token = mappers.to_list_nodes_command(pb.ListNodesRequest(page_size=page_size))
        assert command.limit == limit and command.offset == 0 and token is None

    def test_negative_page_size_is_invalid(self) -> None:
        with pytest.raises(InvalidReadRequestError):
            mappers.to_list_nodes_command(pb.ListNodesRequest(page_size=-1))

    def test_blank_filters_are_ignored(self) -> None:
        command, _ = mappers.to_list_nodes_command(pb.ListNodesRequest(domain=" ", profile_id=""))
        assert command == ListNodesCommand(limit=100)

    def test_page_token_sets_offset(self) -> None:
        token = PageToken(graph_version=GRAPH_VERSION, domain="algebra", profile_id="", offset=40).encode()
        command, decoded = mappers.to_list_nodes_command(pb.ListNodesRequest(domain="algebra", page_token=token))
        assert command.offset == 40 and decoded is not None and decoded.graph_version == GRAPH_VERSION

    @pytest.mark.parametrize(
        "request_filters",
        [{"domain": "geometry"}, {"profile_id": "profile.core"}, {"domain": "algebra", "profile_id": "x"}],
    )
    def test_page_token_must_match_filters(self, request_filters: dict) -> None:
        token = PageToken(graph_version=GRAPH_VERSION, domain="algebra", profile_id="", offset=1).encode()
        with pytest.raises(InvalidReadRequestError, match="filters"):
            mappers.to_list_nodes_command(pb.ListNodesRequest(page_token=token, **request_filters))


class TestPageToken:
    def test_round_trip(self) -> None:
        token = PageToken(graph_version="v", domain="d", profile_id="p", offset=7)
        assert PageToken.decode(token.encode()) == token

    def test_encoding_is_url_safe_and_unpadded(self) -> None:
        encoded = PageToken(graph_version="v" * 7, domain="", profile_id="", offset=1).encode()
        assert "=" not in encoded and "+" not in encoded and "/" not in encoded

    @pytest.mark.parametrize(
        "token",
        [
            "not-base64!!",
            "e30",  # {}
            "WzFd",  # [1]
            "eyJ2IjoidiIsImQiOiIiLCJwIjoiIiwibyI6Ii0xIn0",  # offset "-1"
            "eyJ2IjoidiIsImQiOiIiLCJwIjoiIiwibyI6IngifQ",  # offset "x"
        ],
    )
    def test_malformed_tokens_are_invalid_requests(self, token: str) -> None:
        with pytest.raises(InvalidReadRequestError, match="malformed"):
            PageToken.decode(token)


# ---------------------------------------------------------------------------
# Results -> responses
# ---------------------------------------------------------------------------

class TestResponseMapping:
    @pytest.mark.parametrize(
        "level,name,expected",
        [
            (0, "UNEXPOSED", pb.MASTERY_LEVEL_UNEXPOSED),
            (1, "RECOGNISES", pb.MASTERY_LEVEL_RECOGNISES),
            (2, "GUIDED", pb.MASTERY_LEVEL_GUIDED),
            (3, "INDEPENDENT", pb.MASTERY_LEVEL_INDEPENDENT),
            (4, "EFFICIENT", pb.MASTERY_LEVEL_EFFICIENT),
            (5, "TRANSFERABLE", pb.MASTERY_LEVEL_TRANSFERABLE),
        ],
    )
    def test_every_mastery_level_maps_to_proto_enum(self, level: int, name: str, expected: int) -> None:
        view = NodeView(
            id="n", name="N", domain="d", description="x",
            mastery_criteria=(MasteryCriterionView(level=level, level_name=name, description="desc"),),
            error_taxonomy=(), prerequisite_ids=(), regression_ids=(),
        )
        message = mappers.to_node_message(view)
        assert message.mastery_criteria[0].level == expected
        assert message.mastery_criteria[0].description == "desc"

    def test_node_message_copies_all_fields(self, use_case: ReadGraphUseCase) -> None:
        response = mappers.to_get_node_response(use_case.execute(GetNodeCommand(node_id="b.quadratics")))
        node = response.node
        assert response.graph_version == GRAPH_VERSION
        assert (node.id, node.name, node.domain) == ("b.quadratics", "Quadratics", "algebra")
        assert list(node.error_taxonomy) == ["b.quadratics.misconception"]
        assert list(node.regression_ids) == ["b.linear-equations"]
        assert [c.level for c in node.mastery_criteria] == [pb.MASTERY_LEVEL_RECOGNISES, pb.MASTERY_LEVEL_INDEPENDENT]

    def test_metadata_response(self, use_case: ReadGraphUseCase) -> None:
        response = mappers.to_get_graph_metadata_response(use_case.execute(GetGraphMetadataCommand()))
        assert response.graph_version == GRAPH_VERSION
        assert (response.node_count, response.edge_count, response.profile_count) == (6, 5, 1)
        assert list(response.domains) == ["algebra", "arithmetic", "geometry"]
        assert list(response.profile_ids) == ["profile.core"]

    def test_prerequisite_kinds(self, use_case: ReadGraphUseCase) -> None:
        response = mappers.to_get_prerequisites_response(
            use_case.execute(GetPrerequisitesCommand(node_id="b.linear-equations"))
        )
        assert [p.kind for p in response.prerequisites] == [pb.PREREQUISITE_KIND_HARD, pb.PREREQUISITE_KIND_SOFT]

    def test_empty_results_keep_graph_version(self, use_case: ReadGraphUseCase) -> None:
        prereqs = mappers.to_get_prerequisites_response(use_case.execute(GetPrerequisitesCommand(node_id="a.counting")))
        targets = mappers.to_get_regression_targets_response(
            use_case.execute(GetRegressionTargetsCommand(node_id="c.isolated"))
        )
        command = ListNodesCommand(domain="topology")
        listing = mappers.to_list_nodes_response(use_case.execute(command), command)
        for response in (prereqs, targets, listing):
            assert response.graph_version == GRAPH_VERSION
        assert listing.total_size == 0 and listing.next_page_token == ""

    def test_list_nodes_next_token_encodes_next_page(self, use_case: ReadGraphUseCase) -> None:
        command = ListNodesCommand(domain="arithmetic", limit=2)
        response = mappers.to_list_nodes_response(use_case.execute(command), command)
        token = PageToken.decode(response.next_page_token)
        assert token == PageToken(graph_version=GRAPH_VERSION, domain="arithmetic", profile_id="", offset=2)
        assert response.total_size == 3

    def test_unreachable_path(self, use_case: ReadGraphUseCase) -> None:
        response = mappers.to_get_learning_path_response(
            use_case.execute(
                GetLearningPathCommand(start_node_id="c.isolated", target_node_id="a.counting", include_soft=True)
            )
        )
        assert response.path_found is False and len(response.path) == 0
        assert response.graph_version == GRAPH_VERSION

    @pytest.mark.parametrize(
        "ready,version,status,expected_version",
        [
            (True, "v1", pb.HealthCheckResponse.SERVING_STATUS_SERVING, "v1"),
            (False, None, pb.HealthCheckResponse.SERVING_STATUS_NOT_SERVING, ""),
        ],
    )
    def test_health_check(self, ready: bool, version: str | None, status: int, expected_version: str) -> None:
        response = mappers.to_health_check_response(ready, version)
        assert response.status == status and response.graph_version == expected_version
