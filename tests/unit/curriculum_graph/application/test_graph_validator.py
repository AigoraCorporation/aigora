import pytest

from aigora.curriculum_graph.application.graph_validator import GraphValidator
from aigora.curriculum_graph.application.validation_errors import (
    CyclicDependencyError,
    InvalidEdgeReferenceError,
    InvalidNodeIdFormatError,
    InvalidNodeMasteryDefinitionError,
    InvalidProfileIdFormatError,
    InvalidProfileMasteryTargetError,
    InvalidProfileProgressionPathError,
    InvalidProfileReferenceError,
    InvalidProfileWeightError,
)
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.node import Node


def make_mastery_scale(*levels: MasteryLevel) -> MasteryScale:
    return MasteryScale(
        criteria_by_level={
            level: MasteryCriterion(
                level=level,
                description=f"Description for {level.name}",
            )
            for level in levels
        }
    )


def make_node(
    node_id: str,
    *levels: MasteryLevel,
) -> Node:
    return Node(
        id=node_id,
        name=node_id.split(".")[-1].replace("-", " ").title(),
        domain="mathematics",
        description=f"{node_id} description",
        mastery_criteria=make_mastery_scale(*levels),
    )


def make_edge(
    source: str,
    target: str,
    edge_type: EdgeType = EdgeType.HARD_PREREQUISITE,
) -> Edge:
    return Edge(
        type=edge_type,
        source=source,
        target=target,
    )


def make_profile(
    profile_id: str = "profile.sat-math",
    *,
    required_nodes: set[str] | None = None,
    mastery_targets: dict[str, MasteryLevel] | None = None,
    node_weights: dict[str, float] | None = None,
    progression_path: list[str] | None = None,
) -> CurriculumProfile:
    return CurriculumProfile(
        id=profile_id,
        name="SAT Math",
        required_nodes=required_nodes or set(),
        mastery_targets=mastery_targets or {},
        node_weights=node_weights or {},
        progression_path=progression_path or [],
    )


def test_should_validate_valid_graph_successfully():
    validator = GraphValidator()
    graph = CurriculumGraph()

    fractions = make_node(
        "math.arithmetic.fractions",
        MasteryLevel.RECOGNISES,
        MasteryLevel.INDEPENDENT,
    )
    equations = make_node(
        "math.algebra.linear-equations",
        MasteryLevel.GUIDED,
        MasteryLevel.EFFICIENT,
    )

    graph.add_node(fractions)
    graph.add_node(equations)
    graph.add_edge(
        make_edge(
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
        )
    )

    profile = make_profile(
        required_nodes={
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
        },
        mastery_targets={
            "math.arithmetic.fractions": MasteryLevel.INDEPENDENT,
            "math.algebra.linear-equations": MasteryLevel.EFFICIENT,
        },
        node_weights={
            "math.arithmetic.fractions": 1.0,
            "math.algebra.linear-equations": 2.0,
        },
        progression_path=[
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
        ],
    )
    graph.add_profile(profile)

    validator.validate(graph)


def test_should_raise_error_for_invalid_node_id_format():
    validator = GraphValidator()
    graph = CurriculumGraph()

    invalid_node = Node(
        id="fractions",
        name="Fractions",
        domain="math",
        description="fractions description",
        mastery_criteria=make_mastery_scale(MasteryLevel.RECOGNISES),
    )
    graph.add_node(invalid_node)

    with pytest.raises(
        InvalidNodeIdFormatError,
        match="Node id does not conform to the expected format",
    ):
        validator.validate(graph)


def test_should_raise_error_for_invalid_profile_id_format():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.arithmetic.fractions",
            MasteryLevel.RECOGNISES,
        )
    )

    graph.add_profile(
        make_profile(
            profile_id="sat-math",
            required_nodes={"math.arithmetic.fractions"},
        )
    )

    with pytest.raises(
        InvalidProfileIdFormatError,
        match="Profile id does not conform to the expected format",
    ):
        validator.validate(graph)


def test_should_raise_error_for_edge_with_unknown_source():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.algebra.linear-equations",
            MasteryLevel.GUIDED,
        )
    )
    graph.add_edge(
        make_edge(
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
        )
    )

    with pytest.raises(
        InvalidEdgeReferenceError,
        match="Edge source references unknown node",
    ):
        validator.validate(graph)


def test_should_raise_error_for_edge_with_unknown_target():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.arithmetic.fractions",
            MasteryLevel.RECOGNISES,
        )
    )
    graph.add_edge(
        make_edge(
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
        )
    )

    with pytest.raises(
        InvalidEdgeReferenceError,
        match="Edge target references unknown node",
    ):
        validator.validate(graph)


def test_should_raise_error_for_cyclic_prerequisite_dependency():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.arithmetic.fractions",
            MasteryLevel.RECOGNISES,
        )
    )
    graph.add_node(
        make_node(
            "math.algebra.linear-equations",
            MasteryLevel.GUIDED,
        )
    )

    graph.add_edge(
        make_edge(
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
        )
    )
    graph.add_edge(
        make_edge(
            "math.algebra.linear-equations",
            "math.arithmetic.fractions",
        )
    )

    with pytest.raises(
        CyclicDependencyError,
        match="Cyclic prerequisite dependency detected",
    ):
        validator.validate(graph)

def test_should_raise_error_for_profile_referencing_unknown_node():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.arithmetic.fractions",
            MasteryLevel.RECOGNISES,
        )
    )

    profile = make_profile(
        required_nodes={
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
        }
    )
    graph.add_profile(profile)

    with pytest.raises(
        InvalidProfileReferenceError,
        match="references unknown node",
    ):
        validator.validate(graph)


def test_should_raise_error_for_profile_mastery_target_with_unexposed_level():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.arithmetic.fractions",
            MasteryLevel.RECOGNISES,
            MasteryLevel.INDEPENDENT,
        )
    )

    profile = make_profile(
        mastery_targets={
            "math.arithmetic.fractions": MasteryLevel.UNEXPOSED,
        }
    )
    graph.add_profile(profile)

    with pytest.raises(
        InvalidProfileMasteryTargetError,
        match="UNEXPOSED is not a valid curriculum target",
    ):
        validator.validate(graph)


def test_should_raise_error_for_profile_mastery_target_not_supported_by_node():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.arithmetic.fractions",
            MasteryLevel.RECOGNISES,
        )
    )

    profile = make_profile(
        mastery_targets={
            "math.arithmetic.fractions": MasteryLevel.EFFICIENT,
        }
    )
    graph.add_profile(profile)

    with pytest.raises(
        InvalidProfileMasteryTargetError,
        match="targets unsupported mastery level",
    ):
        validator.validate(graph)


def test_should_raise_error_for_profile_weight_equal_to_zero():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.arithmetic.fractions",
            MasteryLevel.RECOGNISES,
        )
    )

    profile = make_profile(
        node_weights={
            "math.arithmetic.fractions": 0.0,
        }
    )
    graph.add_profile(profile)

    with pytest.raises(
        InvalidProfileWeightError,
        match="Weights must be strictly positive",
    ):
        validator.validate(graph)

def test_should_raise_error_for_profile_progression_path_with_unknown_node():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.arithmetic.fractions",
            MasteryLevel.RECOGNISES,
        )
    )

    profile = make_profile(
        progression_path=[
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
        ]
    )
    graph.add_profile(profile)

    with pytest.raises(
        InvalidProfileReferenceError,
        match="references unknown node",
    ):
        validator.validate(graph)


def test_should_raise_error_for_progression_path_violating_prerequisite_order():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.arithmetic.fractions",
            MasteryLevel.RECOGNISES,
        )
    )
    graph.add_node(
        make_node(
            "math.algebra.linear-equations",
            MasteryLevel.GUIDED,
        )
    )

    graph.add_edge(
        make_edge(
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
            EdgeType.HARD_PREREQUISITE,
        )
    )

    profile = make_profile(
        progression_path=[
            "math.algebra.linear-equations",
            "math.arithmetic.fractions",
        ]
    )
    graph.add_profile(profile)

    with pytest.raises(
        InvalidProfileProgressionPathError,
        match="violates prerequisite order",
    ):
        validator.validate(graph)


def test_should_allow_soft_prerequisite_without_progression_order_enforcement():
    validator = GraphValidator()
    graph = CurriculumGraph()

    graph.add_node(
        make_node(
            "math.arithmetic.fractions",
            MasteryLevel.RECOGNISES,
        )
    )
    graph.add_node(
        make_node(
            "math.algebra.linear-equations",
            MasteryLevel.GUIDED,
        )
    )

    graph.add_edge(
        make_edge(
            "math.arithmetic.fractions",
            "math.algebra.linear-equations",
            EdgeType.SOFT_PREREQUISITE,
        )
    )

    profile = make_profile(
        progression_path=[
            "math.algebra.linear-equations",
            "math.arithmetic.fractions",
        ]
    )
    graph.add_profile(profile)

    validator.validate(graph)