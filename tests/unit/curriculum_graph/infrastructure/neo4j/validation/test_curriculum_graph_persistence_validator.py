"""Unit tests for CurriculumGraphPersistenceValidator."""
from __future__ import annotations

import pytest

from aigora.curriculum_graph.infrastructure.neo4j.errors import (
    GraphPersistenceValidationError,
)
from aigora.curriculum_graph.infrastructure.neo4j.validation.curriculum_graph_persistence_validator import (
    CurriculumGraphPersistenceValidator,
    PersistenceValidationResult,
)
from aigora.curriculum_graph.domain.entities.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.entities.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.entities.edge import Edge
from aigora.curriculum_graph.domain.enums.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.value_objects.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.entities.node import Node


def _make_node(node_id: str = "n1") -> Node:
    return Node(
        id=node_id,
        name=f"Node {node_id}",
        domain="math",
        description="A test node",
        mastery_criteria=MasteryScale(
            criteria_by_level={
                MasteryLevel.GUIDED: MasteryCriterion(
                    level=MasteryLevel.GUIDED, description="Guided"
                )
            }
        ),
    )


def _make_graph() -> CurriculumGraph:
    graph = CurriculumGraph()
    graph.add_node(_make_node("n1"))
    graph.add_node(_make_node("n2"))
    graph.add_edge(Edge(type=EdgeType.HARD_PREREQUISITE, source="n1", target="n2"))
    graph.add_profile(CurriculumProfile(id="p1", name="Profile 1", required_nodes={"n1", "n2"}))
    return graph


def _ok_result() -> PersistenceValidationResult:
    return PersistenceValidationResult(
        persisted_node_count=2,
        persisted_edge_count=1,
        found_node_ids={"n1", "n2"},
        found_profile_ids={"p1"},
    )


class TestCurriculumGraphPersistenceValidator:
    @pytest.fixture
    def validator(self) -> CurriculumGraphPersistenceValidator:
        return CurriculumGraphPersistenceValidator()

    def test_happy_path_does_not_raise(
        self, validator: CurriculumGraphPersistenceValidator
    ) -> None:
        graph = _make_graph()
        validator.validate(graph, _ok_result())  # must not raise

    def test_node_count_mismatch_raises(
        self, validator: CurriculumGraphPersistenceValidator
    ) -> None:
        graph = _make_graph()
        result = _ok_result()
        result.persisted_node_count = 1  # expected 2
        with pytest.raises(GraphPersistenceValidationError, match="Node count mismatch"):
            validator.validate(graph, result)

    def test_edge_count_mismatch_raises(
        self, validator: CurriculumGraphPersistenceValidator
    ) -> None:
        graph = _make_graph()
        result = _ok_result()
        result.persisted_edge_count = 0  # expected 1
        with pytest.raises(GraphPersistenceValidationError, match="Edge count mismatch"):
            validator.validate(graph, result)

    def test_missing_node_ids_raises(
        self, validator: CurriculumGraphPersistenceValidator
    ) -> None:
        graph = _make_graph()
        result = _ok_result()
        result.found_node_ids = {"n1"}  # missing n2
        with pytest.raises(GraphPersistenceValidationError, match="Missing persisted node IDs"):
            validator.validate(graph, result)

    def test_missing_profile_ids_raises(
        self, validator: CurriculumGraphPersistenceValidator
    ) -> None:
        graph = _make_graph()
        result = _ok_result()
        result.found_profile_ids = set()  # missing p1
        with pytest.raises(GraphPersistenceValidationError, match="Missing persisted profile IDs"):
            validator.validate(graph, result)

    def test_no_profiles_skips_profile_check(
        self, validator: CurriculumGraphPersistenceValidator
    ) -> None:
        graph = CurriculumGraph()
        graph.add_node(_make_node("n1"))
        result = PersistenceValidationResult(
            persisted_node_count=1,
            persisted_edge_count=0,
            found_node_ids={"n1"},
            found_profile_ids=set(),
        )
        validator.validate(graph, result)  # must not raise — no profiles expected

    def test_greater_persisted_count_is_accepted(
        self, validator: CurriculumGraphPersistenceValidator
    ) -> None:
        graph = _make_graph()
        result = _ok_result()
        result.persisted_node_count = 5  # more than expected — acceptable
        result.persisted_edge_count = 3
        validator.validate(graph, result)  # must not raise
