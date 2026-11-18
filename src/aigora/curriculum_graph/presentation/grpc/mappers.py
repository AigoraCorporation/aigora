"""Mapping between gRPC messages (aigora.curriculum_graph.v1) and application commands/results."""
from __future__ import annotations

import base64
import binascii
import json
from dataclasses import dataclass

from aigora.curriculum_graph.application.errors.read_graph_errors import InvalidReadRequestError
from aigora.curriculum_graph.application.use_cases.read_graph import (
    MAX_PAGE_SIZE,
    GetGraphMetadataCommand,
    GetGraphMetadataResult,
    GetLearningPathCommand,
    GetLearningPathResult,
    GetNodeCommand,
    GetNodeResult,
    GetPrerequisitesCommand,
    GetPrerequisitesResult,
    GetRegressionTargetsCommand,
    GetRegressionTargetsResult,
    ListNodesCommand,
    ListNodesResult,
    NodeView,
    PrerequisiteKind,
)
from aigora.curriculum_graph.v1 import curriculum_graph_pb2 as pb

DEFAULT_PAGE_SIZE = 100

_PREREQUISITE_KIND = {
    PrerequisiteKind.HARD: pb.PREREQUISITE_KIND_HARD,
    PrerequisiteKind.SOFT: pb.PREREQUISITE_KIND_SOFT,
}


# ---------------------------------------------------------------------------
# Requests -> commands
# ---------------------------------------------------------------------------

def expected_version(context: pb.RequestContext) -> str | None:
    return context.graph_version.strip() or None


def _include_soft(request) -> bool:
    return request.include_soft if request.HasField("include_soft") else True


def to_get_graph_metadata_command(request: pb.GetGraphMetadataRequest) -> GetGraphMetadataCommand:
    return GetGraphMetadataCommand(expected_version=expected_version(request.context))


def to_get_node_command(request: pb.GetNodeRequest) -> GetNodeCommand:
    return GetNodeCommand(node_id=request.node_id.strip(), expected_version=expected_version(request.context))


def to_get_prerequisites_command(request: pb.GetPrerequisitesRequest) -> GetPrerequisitesCommand:
    return GetPrerequisitesCommand(
        node_id=request.node_id.strip(),
        include_soft=_include_soft(request),
        expected_version=expected_version(request.context),
    )


def to_get_regression_targets_command(request: pb.GetRegressionTargetsRequest) -> GetRegressionTargetsCommand:
    return GetRegressionTargetsCommand(
        node_id=request.node_id.strip(), expected_version=expected_version(request.context)
    )


def to_get_learning_path_command(request: pb.GetLearningPathRequest) -> GetLearningPathCommand:
    return GetLearningPathCommand(
        start_node_id=request.start_node_id.strip(),
        target_node_id=request.target_node_id.strip(),
        include_soft=_include_soft(request),
        expected_version=expected_version(request.context),
    )


@dataclass(frozen=True)
class PageToken:
    """Opaque ListNodes cursor, bound to the graph version and filters."""

    graph_version: str
    domain: str
    profile_id: str
    offset: int

    def encode(self) -> str:
        raw = json.dumps(
            {"v": self.graph_version, "d": self.domain, "p": self.profile_id, "o": self.offset},
            separators=(",", ":"),
        ).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    @classmethod
    def decode(cls, token: str) -> PageToken:
        try:
            padded = token + "=" * (-len(token) % 4)
            data = json.loads(base64.urlsafe_b64decode(padded.encode()))
            parsed = cls(
                graph_version=str(data["v"]), domain=str(data["d"]), profile_id=str(data["p"]), offset=int(data["o"])
            )
        except (binascii.Error, ValueError, KeyError, TypeError) as exc:
            raise InvalidReadRequestError("page_token is malformed.") from exc
        if parsed.offset < 0:
            raise InvalidReadRequestError("page_token is malformed.")
        return parsed


def to_list_nodes_command(request: pb.ListNodesRequest) -> tuple[ListNodesCommand, PageToken | None]:
    """Return the command and the decoded page token (if any) for post-validation."""
    if request.page_size < 0:
        raise InvalidReadRequestError("page_size must not be negative.")
    limit = min(request.page_size or DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE)
    domain = request.domain.strip()
    profile_id = request.profile_id.strip()
    token = PageToken.decode(request.page_token) if request.page_token else None
    if token is not None and (token.domain != domain or token.profile_id != profile_id):
        raise InvalidReadRequestError("page_token does not match the request filters.")
    command = ListNodesCommand(
        domain=domain or None,
        profile_id=profile_id or None,
        offset=token.offset if token else 0,
        limit=limit,
        expected_version=expected_version(request.context),
    )
    return command, token


# ---------------------------------------------------------------------------
# Results -> responses
# ---------------------------------------------------------------------------

def to_node_message(node: NodeView) -> pb.Node:
    return pb.Node(
        id=node.id,
        name=node.name,
        domain=node.domain,
        description=node.description,
        mastery_criteria=[
            pb.MasteryCriterion(level=pb.MasteryLevel.Value(f"MASTERY_LEVEL_{c.level_name}"), description=c.description)
            for c in node.mastery_criteria
        ],
        error_taxonomy=list(node.error_taxonomy),
        prerequisite_ids=list(node.prerequisite_ids),
        regression_ids=list(node.regression_ids),
    )


def to_get_graph_metadata_response(result: GetGraphMetadataResult) -> pb.GetGraphMetadataResponse:
    meta = result.metadata
    return pb.GetGraphMetadataResponse(
        graph_version=result.graph_version,
        node_count=meta.node_count,
        edge_count=meta.edge_count,
        profile_count=meta.profile_count,
        profile_ids=list(meta.profile_ids),
        domains=list(meta.domains),
    )


def to_get_node_response(result: GetNodeResult) -> pb.GetNodeResponse:
    return pb.GetNodeResponse(graph_version=result.graph_version, node=to_node_message(result.node))


def to_list_nodes_response(result: ListNodesResult, command: ListNodesCommand) -> pb.ListNodesResponse:
    next_token = ""
    if result.next_offset is not None:
        next_token = PageToken(
            graph_version=result.graph_version,
            domain=command.domain or "",
            profile_id=command.profile_id or "",
            offset=result.next_offset,
        ).encode()
    return pb.ListNodesResponse(
        graph_version=result.graph_version,
        nodes=[to_node_message(node) for node in result.nodes],
        next_page_token=next_token,
        total_size=result.total_size,
    )


def to_get_prerequisites_response(result: GetPrerequisitesResult) -> pb.GetPrerequisitesResponse:
    return pb.GetPrerequisitesResponse(
        graph_version=result.graph_version,
        prerequisites=[
            pb.Prerequisite(node=to_node_message(p.node), kind=_PREREQUISITE_KIND[p.kind]) for p in result.prerequisites
        ],
    )


def to_get_regression_targets_response(result: GetRegressionTargetsResult) -> pb.GetRegressionTargetsResponse:
    return pb.GetRegressionTargetsResponse(
        graph_version=result.graph_version, targets=[to_node_message(node) for node in result.targets]
    )


def to_get_learning_path_response(result: GetLearningPathResult) -> pb.GetLearningPathResponse:
    return pb.GetLearningPathResponse(
        graph_version=result.graph_version,
        path_found=result.path_found,
        path=[to_node_message(node) for node in result.path],
    )


def to_health_check_response(ready: bool, graph_version: str | None) -> pb.HealthCheckResponse:
    status = (
        pb.HealthCheckResponse.SERVING_STATUS_SERVING if ready else pb.HealthCheckResponse.SERVING_STATUS_NOT_SERVING
    )
    return pb.HealthCheckResponse(status=status, graph_version=graph_version or "")
