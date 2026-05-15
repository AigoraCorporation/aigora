from __future__ import annotations

from pathlib import Path

import pytest

from aigora.curriculum_graph.application.errors.load_graph_errors import InvalidGraphVersionError
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_context import (
    GraphLoadingContext,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.graph_loading_pipeline import (
    GraphLoadingPipeline,
)
from aigora.curriculum_graph.application.use_cases.load_graph.pipeline.steps import (
    AssembleGraphStep,
    MapGraphStep,
    ParseGraphStep,
    ValidateGraphStep,
    ValidateSchemaStep,
    ValidateVersionStep,
)
from tests.unit.curriculum_graph.application.use_cases.load_graph.test_load_graph_use_case import (
    FakeAssembler,
    FakeMapper,
    FakeParser,
    FakeSchemaValidator,
    FakeValidator,
    FakeVersionValidator,
    make_payload,
)


def test_pipeline_should_execute_steps_in_order():
    calls: list[str] = []

    class Step:
        def __init__(self, name: str) -> None:
            self._name = name

        def execute(self, context: GraphLoadingContext) -> None:
            calls.append(self._name)
            if self._name == "last":
                context.graph = object()

    context = GraphLoadingContext(file_path=Path("graph.yaml"))

    result = GraphLoadingPipeline([Step("first"), Step("last")]).execute(context)

    assert calls == ["first", "last"]
    assert result is context.graph


def test_pipeline_should_raise_when_no_graph_is_produced():
    class NoopStep:
        def execute(self, context: GraphLoadingContext) -> None:
            return None

    with pytest.raises(ValueError, match="without producing a graph"):
        GraphLoadingPipeline([NoopStep()]).execute(
            GraphLoadingContext(file_path=Path("graph.yaml"))
        )


def test_parse_step_should_store_payload_on_context():
    payload = make_payload()
    context = GraphLoadingContext(file_path=Path("graph.yaml"))
    parser = FakeParser(payload)

    ParseGraphStep(parser).execute(context)

    assert parser.called_with == Path("graph.yaml")
    assert context.payload is payload


def test_schema_step_should_raise_when_payload_was_not_parsed():
    with pytest.raises(ValueError, match="must be parsed before schema validation"):
        ValidateSchemaStep(FakeSchemaValidator()).execute(
            GraphLoadingContext(file_path=Path("graph.yaml"))
        )


def test_schema_step_should_delegate_to_validator():
    payload = make_payload()
    validator = FakeSchemaValidator()
    context = GraphLoadingContext(file_path=Path("graph.yaml"), payload=payload)

    ValidateSchemaStep(validator).execute(context)

    assert validator.received_payload is payload


def test_map_step_should_raise_when_payload_was_not_parsed():
    with pytest.raises(ValueError, match="must be parsed before mapping"):
        MapGraphStep(FakeMapper()).execute(GraphLoadingContext(file_path=Path("graph.yaml")))


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"nodes": [], "edges": []}, "version.*required"),
        ({"version": 123, "nodes": [], "edges": []}, "version.*string"),
    ],
)
def test_map_step_should_validate_version(payload, message):
    with pytest.raises(InvalidGraphVersionError, match=message):
        MapGraphStep(FakeMapper()).execute(
            GraphLoadingContext(file_path=Path("graph.yaml"), payload=payload)
        )


def test_map_step_should_populate_domain_parts_on_context():
    context = GraphLoadingContext(file_path=Path("graph.yaml"), payload=make_payload())
    mapper = FakeMapper()

    MapGraphStep(mapper).execute(context)

    assert context.nodes == [mapper.node]
    assert context.edges == [mapper.edge]
    assert context.profiles == [mapper.profile]
    assert context.version == "0.2.0"


def test_assemble_step_should_store_graph_on_context():
    context = GraphLoadingContext(file_path=Path("graph.yaml"), version="0.2.0")
    assembler = FakeAssembler()

    AssembleGraphStep(assembler).execute(context)

    assert context.graph is assembler.graph
    assert assembler.received_version == "0.2.0"


def test_validate_graph_step_should_raise_when_graph_was_not_assembled():
    with pytest.raises(ValueError, match="before graph validation"):
        ValidateGraphStep(FakeValidator()).execute(GraphLoadingContext(file_path=Path("graph.yaml")))


def test_validate_graph_step_should_delegate_to_validator():
    assembler = FakeAssembler()
    validator = FakeValidator()
    context = GraphLoadingContext(file_path=Path("graph.yaml"), graph=assembler.graph)

    ValidateGraphStep(validator).execute(context)

    assert validator.received_graph is assembler.graph


def test_validate_version_step_should_raise_when_graph_was_not_assembled():
    with pytest.raises(ValueError, match="before version validation"):
        ValidateVersionStep(FakeVersionValidator()).execute(GraphLoadingContext(file_path=Path("graph.yaml")))


def test_validate_version_step_should_delegate_to_validator():
    assembler = FakeAssembler()
    validator = FakeVersionValidator()
    context = GraphLoadingContext(file_path=Path("graph.yaml"), graph=assembler.graph)

    ValidateVersionStep(validator).execute(context)

    assert validator.received_graph is assembler.graph
