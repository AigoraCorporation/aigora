from __future__ import annotations

from pathlib import Path

import yaml

from ...domain.enums import EdgeType, NodeStatus, ProfileStatus
from ...domain.models import (
    CanonicalGraph,
    CanonicalNode,
    CurriculumProfile,
    ErrorTaxonomyEntry,
    ExamSkillOverlayEntry,
    MasteryCriteria,
    PrerequisiteEdge,
    ProfileNode,
)


class GraphLoadError(Exception):
    """Raised when the graph directory or a graph file cannot be loaded."""


class YAMLGraphLoader:
    """
    Loads a CanonicalGraph from a filesystem directory of YAML files.

    Expected layout:
        <graph_dir>/
            metadata.yaml
            nodes/
                <domain>/
                    <subtopic>/
                        <concept>.yaml
            profiles/
                profile.<name>.yaml

    The loader does not validate the graph. Structural validation is the
    responsibility of StructuralValidator, run by the repository after loading.
    """

    def load(self, graph_dir: Path) -> CanonicalGraph:
        graph_dir = Path(graph_dir)
        if not graph_dir.is_dir():
            raise GraphLoadError(f"Graph directory not found: {graph_dir}")

        metadata = self._load_metadata(graph_dir / "metadata.yaml")
        nodes = self._load_nodes(graph_dir / "nodes")
        profiles = self._load_profiles(graph_dir / "profiles")

        return CanonicalGraph(
            version=metadata["version"],
            published_at=metadata.get("published_at", ""),
            description=metadata.get("description", ""),
            nodes=nodes,
            profiles=profiles,
        )

    # ── Metadata ──────────────────────────────────────────────────────────────

    def _load_metadata(self, path: Path) -> dict:
        if not path.is_file():
            raise GraphLoadError(f"metadata.yaml not found at: {path}")
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict) or "version" not in data:
            raise GraphLoadError("metadata.yaml must contain a 'version' field.")
        return data

    # ── Nodes ─────────────────────────────────────────────────────────────────

    def _load_nodes(self, nodes_dir: Path) -> dict[str, CanonicalNode]:
        if not nodes_dir.is_dir():
            return {}
        nodes: dict[str, CanonicalNode] = {}
        for yaml_file in sorted(nodes_dir.rglob("*.yaml")):
            node = self._parse_node(yaml_file)
            nodes[node.id] = node
        return nodes

    def _parse_node(self, path: Path) -> CanonicalNode:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        try:
            mc_raw = data["mastery_criteria"]
            mastery_criteria = MasteryCriteria(
                level_1=str(mc_raw["1"]),
                level_2=str(mc_raw["2"]),
                level_3=str(mc_raw["3"]),
                level_4=str(mc_raw["4"]),
                level_5=str(mc_raw["5"]),
            )
            error_taxonomy = tuple(
                ErrorTaxonomyEntry(name=e["name"], description=e["description"])
                for e in data.get("error_taxonomy", [])
            )
            prerequisite_ids = tuple(
                PrerequisiteEdge(
                    node_id=p["node_id"],
                    edge_type=EdgeType(p["edge_type"]),
                )
                for p in data.get("prerequisite_ids", [])
            )
            regression_ids = tuple(data.get("regression_ids") or [])

            return CanonicalNode(
                id=data["id"],
                name=data["name"],
                domain=data["domain"],
                description=data["description"],
                mastery_criteria=mastery_criteria,
                error_taxonomy=error_taxonomy,
                prerequisite_ids=prerequisite_ids,
                regression_ids=regression_ids,
                status=NodeStatus(data.get("status", "active")),
                deprecated_since=data.get("deprecated_since"),
                replaced_by=data.get("replaced_by"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GraphLoadError(f"Failed to parse node file '{path}': {exc}") from exc

    # ── Profiles ──────────────────────────────────────────────────────────────

    def _load_profiles(self, profiles_dir: Path) -> dict[str, CurriculumProfile]:
        if not profiles_dir.is_dir():
            return {}
        profiles: dict[str, CurriculumProfile] = {}
        for yaml_file in sorted(profiles_dir.glob("*.yaml")):
            profile = self._parse_profile(yaml_file)
            profiles[profile.id] = profile
        return profiles

    def _parse_profile(self, path: Path) -> CurriculumProfile:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        try:
            required_nodes = tuple(
                ProfileNode(
                    node_id=pn["node_id"],
                    mastery_target=int(pn["mastery_target"]),
                    weight=float(pn["weight"]),
                )
                for pn in data.get("required_nodes", [])
            )
            exam_skill_overlay = tuple(
                ExamSkillOverlayEntry(name=e["name"], description=e["description"])
                for e in data.get("exam_skill_overlay", [])
            )
            return CurriculumProfile(
                id=data["id"],
                name=data["name"],
                version=str(data["version"]),
                requires_graph_version=str(data["requires_graph_version"]),
                required_nodes=required_nodes,
                progression_path=tuple(data.get("progression_path") or []),
                exam_skill_overlay=exam_skill_overlay,
                status=ProfileStatus(data.get("status", "active")),
                retired_at=data.get("retired_at"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise GraphLoadError(
                f"Failed to parse profile file '{path}': {exc}"
            ) from exc
