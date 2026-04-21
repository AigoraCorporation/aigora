from __future__ import annotations

from dataclasses import dataclass, field

from .curriculum_profile import CurriculumProfile
from .edge import Edge
from .enums import EdgeType
from .node import Node


@dataclass(slots=True)
class CurriculumGraph:
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    profiles: dict[str, CurriculumProfile] = field(default_factory=dict)
    version: str | None = field(default=None)

    def add_node(self, node: Node) -> None:
        if node.id in self.nodes:
            raise ValueError(f"Duplicate node id: {node.id}")
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)

    def add_profile(self, profile: CurriculumProfile) -> None:
        if profile.id in self.profiles:
            raise ValueError(f"Duplicate profile id: {profile.id}")
        self.profiles[profile.id] = profile

    def get_node(self, node_id: str) -> Node:
        try:
            return self.nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"Node not found: {node_id}") from exc

    def get_profile(self, profile_id: str) -> CurriculumProfile:
        try:
            return self.profiles[profile_id]
        except KeyError as exc:
            raise KeyError(f"Profile not found: {profile_id}") from exc

    def outgoing_edges(self, node_id: str) -> list[Edge]:
        return [edge for edge in self.edges if edge.source == node_id]

    def incoming_edges(self, node_id: str) -> list[Edge]:
        return [edge for edge in self.edges if edge.target == node_id]

    def edges_by_type(self, edge_type: EdgeType) -> list[Edge]:
        return [edge for edge in self.edges if edge.type == edge_type]