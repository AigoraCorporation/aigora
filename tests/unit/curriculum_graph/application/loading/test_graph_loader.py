import pytest

from aigora.curriculum_graph.application.loading.graph_loader import GraphLoader
from aigora.curriculum_graph.application.loading.loader_errors import GraphLoaderError
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph
from aigora.curriculum_graph.domain.curriculum_profile import CurriculumProfile
from aigora.curriculum_graph.domain.edge import Edge
from aigora.curriculum_graph.domain.enums import EdgeType, MasteryLevel
from aigora.curriculum_graph.domain.mastery import MasteryCriterion, MasteryScale
from aigora.curriculum_graph.domain.node import Node


def make_mastery_scale() -> MasteryScale:
    return MasteryScale(
        criteria_by_level={
            MasteryLevel.RECOGNISES: MasteryCriterion(
                level=MasteryLevel.RECOGNISES,
                description="Recognises the concept.",
            )
        }
    )


def make_node(node_id: str) -> Node:
    return Node(
        id=node_id,
        name=node_id.title(),
        domain="math",
        description=f"{node_id} description",
        mastery_criteria=make_mastery_scale(),
    )


def make_edge(source: str, target: str) -> Edge:
    return Edge(
        type=EdgeType.HARD_PREREQUISITE,
        source=source,
        target=target,
    )


def make_profile(profile_id: str) -> CurriculumProfile:
    return CurriculumProfile(
        id=profile_id,
        name=profile_id.title(),
        required_nodes={"fractions"},
        mastery_targets={"fractions": MasteryLevel.RECOGNISES},
        node_weights={"fractions": 1.0},
        progression_path=["fractions"],
    )


def make_payload() -> dict:
    return {
        "version": "0.2.0",
        "nodes": [{"id": "fractions"}],
        "edges": [{"source": "fractions", "target": "equations"}],
        "profiles": [{"id": "profile.sat-math"}],
    }


class FakeParser:
    def __init__(self, payload):
        self.payload = payload
        self.called_with = None

    def parse_file(self, file_path):
        self.called_with = file_path
        return self.payload


class FakeSchemaValidator:
    def __init__(self):
        self.received_payload = None

    def validate(self, payload):
        self.received_payload = payload


class FakeMapper:
    def __init__(self, node=None, edge=None, profile=None):
        self.node = node or make_node("fractions")
        self.edge = edge or make_edge("fractions", "equations")
        self.profile = profile or make_profile("profile.sat-math")

        self.mapped_nodes = []
        self.mapped_edges = []
        self.mapped_profiles = []

    def map_node(self, payload):
        self.mapped_nodes.append(payload)
        return self.node

    def map_edge(self, payload):
        self.mapped_edges.append(payload)
        return self.edge

    def map_profile(self, payload):
        self.mapped_profiles.append(payload)
        return self.profile


class FakeAssembler:
    def __init__(self, graph=None):
        self.graph = graph or CurriculumGraph()
        self.received_nodes = None
        self.received_edges = None
        self.received_profiles = None
        self.received_version = None

    def assemble(self, nodes, edges, profiles, version=None):
        self.received_nodes = nodes
        self.received_edges = edges
        self.received_profiles = profiles
        self.received_version = version

        self.graph.version = version

        return self.graph


class FakeValidator:
    def __init__(self):
        self.received_graph = None

    def validate(self, graph):
        self.received_graph = graph


class FakeVersionValidator:
    def __init__(self):
        self.received_graph = None

    def validate(self, graph):
        self.received_graph = graph


def make_loader(
    *,
    payload=None,
    parser=None,
    schema_validator=None,
    mapper=None,
    assembler=None,
    validator=None,
    version_validator=None,
):
    return GraphLoader(
        parser=parser or FakeParser(payload or make_payload()),
        schema_validator=schema_validator or FakeSchemaValidator(),
        mapper=mapper or FakeMapper(),
        assembler=assembler or FakeAssembler(),
        validator=validator or FakeValidator(),
        version_validator=version_validator or FakeVersionValidator(),
    )


def test_should_load_curriculum_graph_successfully():
    payload = make_payload()
    expected_graph = CurriculumGraph()

    parser = FakeParser(payload)
    schema_validator = FakeSchemaValidator()
    mapper = FakeMapper()
    assembler = FakeAssembler(expected_graph)
    validator = FakeValidator()
    version_validator = FakeVersionValidator()

    loader = GraphLoader(
        parser=parser,
        schema_validator=schema_validator,
        mapper=mapper,
        assembler=assembler,
        validator=validator,
        version_validator=version_validator,
    )

    result = loader.load("graph.yaml")

    assert result is expected_graph
    assert parser.called_with == "graph.yaml"
    assert schema_validator.received_payload is payload
    assert len(mapper.mapped_nodes) == 1
    assert len(mapper.mapped_edges) == 1
    assert len(mapper.mapped_profiles) == 1
    assert assembler.received_nodes == [mapper.node]
    assert assembler.received_edges == [mapper.edge]
    assert assembler.received_profiles == [mapper.profile]
    assert assembler.received_version == "0.2.0"
    assert validator.received_graph is expected_graph
    assert version_validator.received_graph is expected_graph


def test_should_load_graph_with_empty_profiles_when_profiles_are_missing():
    payload = {
        "version": "0.2.0",
        "nodes": [{"id": "fractions"}],
        "edges": [{"source": "fractions", "target": "equations"}],
    }

    mapper = FakeMapper()
    assembler = FakeAssembler()
    validator = FakeValidator()
    version_validator = FakeVersionValidator()

    loader = GraphLoader(
        parser=FakeParser(payload),
        schema_validator=FakeSchemaValidator(),
        mapper=mapper,
        assembler=assembler,
        validator=validator,
        version_validator=version_validator,
    )

    result = loader.load("graph.yaml")

    assert len(mapper.mapped_nodes) == 1
    assert len(mapper.mapped_edges) == 1
    assert len(mapper.mapped_profiles) == 0
    assert assembler.received_profiles == []
    assert assembler.received_version == "0.2.0"
    assert validator.received_graph is result
    assert version_validator.received_graph is result


def test_should_raise_graph_loader_error_when_parser_fails():
    class FailingParser:
        def parse_file(self, file_path):
            raise ValueError("parser failed")

    loader = make_loader(parser=FailingParser())

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file: graph.yaml",
    ):
        loader.load("graph.yaml")


def test_should_raise_graph_loader_error_when_schema_validator_fails():
    class FailingSchemaValidator:
        def validate(self, payload):
            raise ValueError("schema failed")

    loader = make_loader(schema_validator=FailingSchemaValidator())

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file: graph.yaml",
    ):
        loader.load("graph.yaml")


def test_should_raise_graph_loader_error_when_mapper_fails():
    class FailingMapper(FakeMapper):
        def map_node(self, payload):
            raise ValueError("mapper failed")

    loader = make_loader(mapper=FailingMapper())

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file: graph.yaml",
    ):
        loader.load("graph.yaml")


def test_should_raise_graph_loader_error_when_assembler_fails():
    class FailingAssembler:
        def assemble(self, nodes, edges, profiles, version=None):
            raise ValueError("assembler failed")

    loader = make_loader(assembler=FailingAssembler())

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file: graph.yaml",
    ):
        loader.load("graph.yaml")


def test_should_raise_graph_loader_error_when_validator_fails():
    class FailingValidator:
        def validate(self, graph):
            raise ValueError("validator failed")

    loader = make_loader(
        assembler=FakeAssembler(CurriculumGraph()),
        validator=FailingValidator(),
    )

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file: graph.yaml",
    ):
        loader.load("graph.yaml")


def test_should_raise_graph_loader_error_when_version_validator_fails():
    class FailingVersionValidator:
        def validate(self, graph):
            raise ValueError("version failed")

    loader = make_loader(
        assembler=FakeAssembler(CurriculumGraph()),
        version_validator=FailingVersionValidator(),
    )

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file: graph.yaml",
    ):
        loader.load("graph.yaml")


def test_should_raise_graph_loader_error_when_version_is_missing():
    payload = {
        "nodes": [{"id": "fractions"}],
        "edges": [],
        "profiles": [],
    }

    loader = make_loader(payload=payload)

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file: graph.yaml",
    ):
        loader.load("graph.yaml")


def test_should_raise_graph_loader_error_when_version_is_not_string():
    payload = {
        "version": 1,
        "nodes": [{"id": "fractions"}],
        "edges": [],
        "profiles": [],
    }

    loader = make_loader(payload=payload)

    with pytest.raises(
        GraphLoaderError,
        match="Failed to load CurriculumGraph from file: graph.yaml",
    ):
        loader.load("graph.yaml")