from __future__ import annotations

import pytest

from aigora.curriculum_graph.application.errors.read_graph_errors import (
    GraphNodeNotFoundError,
    GraphProfileNotFoundError,
    GraphUnavailableError,
    GraphVersionMismatchError,
    InvalidReadRequestError,
)
from aigora.curriculum_graph.application.services.published_graph_provider import PublishedGraphProvider
from aigora.curriculum_graph.application.use_cases.read_graph import (
    GetGraphMetadataCommand,
    GetLearningPathCommand,
    GetNodeCommand,
    GetPrerequisitesCommand,
    GetRegressionTargetsCommand,
    ListNodesCommand,
    PrerequisiteKind,
    ReadGraphUseCase,
)
from tests.fixtures.curriculum_graph.read_graph import GRAPH_VERSION, StaticGraphReader, make_graph


@pytest.fixture
def use_case() -> ReadGraphUseCase:
    provider = PublishedGraphProvider(StaticGraphReader())
    provider.load()
    return ReadGraphUseCase(provider)


def test_metadata_summarises_snapshot(use_case: ReadGraphUseCase) -> None:
    result = use_case.execute(GetGraphMetadataCommand())
    assert result.graph_version == GRAPH_VERSION
    assert (result.metadata.node_count, result.metadata.edge_count, result.metadata.profile_count) == (6, 5, 1)
    assert result.metadata.profile_ids == ("profile.core",)
    assert result.metadata.domains == ("algebra", "arithmetic", "geometry")


def test_get_node_returns_view_with_ordered_mastery(use_case: ReadGraphUseCase) -> None:
    result = use_case.execute(GetNodeCommand(node_id="b.quadratics"))
    node = result.node
    assert result.graph_version == GRAPH_VERSION
    assert node.id == "b.quadratics" and node.domain == "algebra"
    assert [c.level_name for c in node.mastery_criteria] == ["RECOGNISES", "INDEPENDENT"]
    assert node.regression_ids == ("b.linear-equations",)
    assert node.error_taxonomy == ("b.quadratics.misconception",)


def test_get_node_unknown_id_carries_version(use_case: ReadGraphUseCase) -> None:
    with pytest.raises(GraphNodeNotFoundError) as exc:
        use_case.execute(GetNodeCommand(node_id="z.unknown"))
    assert exc.value.graph_version == GRAPH_VERSION


@pytest.mark.parametrize("node_id", ["", "   "])
def test_get_node_blank_id_is_invalid(use_case: ReadGraphUseCase, node_id: str) -> None:
    with pytest.raises(InvalidReadRequestError):
        use_case.execute(GetNodeCommand(node_id=node_id))


def test_list_nodes_orders_by_id_and_paginates(use_case: ReadGraphUseCase) -> None:
    first = use_case.execute(ListNodesCommand(limit=4))
    assert [n.id for n in first.nodes] == ["a.counting", "a.decimals", "a.fractions", "b.linear-equations"]
    assert first.total_size == 6 and first.next_offset == 4
    second = use_case.execute(ListNodesCommand(offset=4, limit=4))
    assert [n.id for n in second.nodes] == ["b.quadratics", "c.isolated"]
    assert second.next_offset is None


def test_list_nodes_filters_by_domain_and_profile(use_case: ReadGraphUseCase) -> None:
    assert [n.id for n in use_case.execute(ListNodesCommand(domain="algebra")).nodes] == [
        "b.linear-equations",
        "b.quadratics",
    ]
    by_profile = use_case.execute(ListNodesCommand(profile_id="profile.core"))
    assert [n.id for n in by_profile.nodes] == ["a.counting", "a.fractions", "b.linear-equations"]
    both = use_case.execute(ListNodesCommand(domain="arithmetic", profile_id="profile.core"))
    assert [n.id for n in both.nodes] == ["a.counting", "a.fractions"]


def test_list_nodes_empty_result_still_versioned(use_case: ReadGraphUseCase) -> None:
    result = use_case.execute(ListNodesCommand(domain="topology"))
    assert result.nodes == () and result.total_size == 0 and result.graph_version == GRAPH_VERSION


def test_list_nodes_unknown_profile(use_case: ReadGraphUseCase) -> None:
    with pytest.raises(GraphProfileNotFoundError) as exc:
        use_case.execute(ListNodesCommand(profile_id="profile.missing"))
    assert exc.value.graph_version == GRAPH_VERSION


@pytest.mark.parametrize("offset,limit", [(-1, 10), (0, 0), (0, 1001)])
def test_list_nodes_invalid_bounds(use_case: ReadGraphUseCase, offset: int, limit: int) -> None:
    with pytest.raises(InvalidReadRequestError):
        use_case.execute(ListNodesCommand(offset=offset, limit=limit))


def test_prerequisites_include_kinds(use_case: ReadGraphUseCase) -> None:
    result = use_case.execute(GetPrerequisitesCommand(node_id="b.linear-equations"))
    assert [(p.node.id, p.kind) for p in result.prerequisites] == [
        ("a.fractions", PrerequisiteKind.HARD),
        ("a.decimals", PrerequisiteKind.SOFT),
    ]


def test_prerequisites_hard_only(use_case: ReadGraphUseCase) -> None:
    result = use_case.execute(GetPrerequisitesCommand(node_id="b.linear-equations", include_soft=False))
    assert [p.node.id for p in result.prerequisites] == ["a.fractions"]


def test_prerequisites_of_root_is_empty_but_versioned(use_case: ReadGraphUseCase) -> None:
    result = use_case.execute(GetPrerequisitesCommand(node_id="a.counting"))
    assert result.prerequisites == () and result.graph_version == GRAPH_VERSION


def test_regression_targets_declared_first_then_edges(use_case: ReadGraphUseCase) -> None:
    result = use_case.execute(GetRegressionTargetsCommand(node_id="b.quadratics"))
    assert [n.id for n in result.targets] == ["b.linear-equations", "a.fractions"]
    assert use_case.execute(GetRegressionTargetsCommand(node_id="c.isolated")).targets == ()


def test_learning_path_follows_prerequisites(use_case: ReadGraphUseCase) -> None:
    result = use_case.execute(GetLearningPathCommand(start_node_id="a.counting", target_node_id="b.quadratics"))
    assert result.path_found
    assert [n.id for n in result.path] == ["a.counting", "a.fractions", "b.linear-equations", "b.quadratics"]


def test_learning_path_hard_only_can_be_unreachable(use_case: ReadGraphUseCase) -> None:
    result = use_case.execute(
        GetLearningPathCommand(start_node_id="a.counting", target_node_id="b.quadratics", include_soft=False)
    )
    assert result.path_found is False and result.path == () and result.graph_version == GRAPH_VERSION


def test_learning_path_same_node(use_case: ReadGraphUseCase) -> None:
    result = use_case.execute(GetLearningPathCommand(start_node_id="c.isolated", target_node_id="c.isolated"))
    assert result.path_found and [n.id for n in result.path] == ["c.isolated"]


def test_learning_path_unknown_endpoint(use_case: ReadGraphUseCase) -> None:
    with pytest.raises(GraphNodeNotFoundError):
        use_case.execute(GetLearningPathCommand(start_node_id="a.counting", target_node_id="z.unknown"))


def test_expected_version_mismatch(use_case: ReadGraphUseCase) -> None:
    with pytest.raises(GraphVersionMismatchError):
        use_case.execute(GetNodeCommand(node_id="a.counting", expected_version="1999.01.0"))


def test_unloaded_graph_is_unavailable() -> None:
    use_case = ReadGraphUseCase(PublishedGraphProvider(StaticGraphReader()))
    with pytest.raises(GraphUnavailableError):
        use_case.execute(GetGraphMetadataCommand())


def test_prerequisite_order_does_not_depend_on_edge_storage_order() -> None:
    graph = make_graph()
    graph.edges.reverse()
    provider = PublishedGraphProvider(StaticGraphReader(graph))
    provider.load()
    result = ReadGraphUseCase(provider).execute(GetPrerequisitesCommand(node_id="b.linear-equations"))
    assert [(p.node.id, p.kind) for p in result.prerequisites] == [
        ("a.fractions", PrerequisiteKind.HARD),
        ("a.decimals", PrerequisiteKind.SOFT),
    ]
