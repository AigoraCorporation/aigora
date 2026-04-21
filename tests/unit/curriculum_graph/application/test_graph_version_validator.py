import pytest

from aigora.curriculum_graph.application.graph_version_validator import GraphVersionValidator
from aigora.curriculum_graph.application.versioning_errors import (
    InvalidVersionFormatError,
    MissingVersionError,
)
from aigora.curriculum_graph.domain.curriculum_graph import CurriculumGraph


# ── Helpers ───────────────────────────────────────────────────────────────────


def make_graph(version: str | None = None) -> CurriculumGraph:
    return CurriculumGraph(version=version)


# ── Happy path ────────────────────────────────────────────────────────────────


def test_should_accept_valid_semver():
    validator = GraphVersionValidator()
    graph = make_graph("1.0.0")
    validator.validate(graph)


def test_should_accept_multi_digit_version_numbers():
    validator = GraphVersionValidator()
    graph = make_graph("10.20.30")
    validator.validate(graph)


def test_should_accept_zero_patch_version():
    validator = GraphVersionValidator()
    graph = make_graph("2.3.0")
    validator.validate(graph)


def test_curriculum_graph_should_carry_version_metadata():
    graph = make_graph("1.0.0")
    assert graph.version == "1.0.0"


def test_version_should_default_to_none():
    graph = CurriculumGraph()
    assert graph.version is None


# ── Edge cases ────────────────────────────────────────────────────────────────


def test_should_preserve_version_through_graph_construction():
    graph = make_graph("1.0.0")
    assert graph.version == "1.0.0"


def test_initial_version_preserved_correctly():
    graph = make_graph("1.0.0")
    validator = GraphVersionValidator()
    validator.validate(graph)
    assert graph.version == "1.0.0"


# ── Failure cases ─────────────────────────────────────────────────────────────


def test_should_raise_error_when_version_is_none():
    validator = GraphVersionValidator()
    graph = make_graph(None)
    with pytest.raises(MissingVersionError, match="missing required version"):
        validator.validate(graph)


def test_should_raise_error_when_version_is_missing_patch():
    validator = GraphVersionValidator()
    graph = make_graph("1.0")
    with pytest.raises(InvalidVersionFormatError):
        validator.validate(graph)


def test_should_raise_error_when_version_has_extra_segment():
    validator = GraphVersionValidator()
    graph = make_graph("1.0.0.0")
    with pytest.raises(InvalidVersionFormatError):
        validator.validate(graph)


def test_should_raise_error_when_version_has_letters():
    validator = GraphVersionValidator()
    graph = make_graph("v1.0.0")
    with pytest.raises(InvalidVersionFormatError):
        validator.validate(graph)


def test_should_raise_error_when_version_is_empty_string():
    validator = GraphVersionValidator()
    graph = make_graph("")
    with pytest.raises(InvalidVersionFormatError):
        validator.validate(graph)


def test_should_raise_error_when_version_has_prerelease_suffix():
    validator = GraphVersionValidator()
    graph = make_graph("1.0.0-alpha")
    with pytest.raises(InvalidVersionFormatError):
        validator.validate(graph)


def test_should_raise_error_when_version_is_only_dots():
    validator = GraphVersionValidator()
    graph = make_graph("...")
    with pytest.raises(InvalidVersionFormatError):
        validator.validate(graph)
