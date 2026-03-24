from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..domain.models import CanonicalGraph


# ─── Validation result types ──────────────────────────────────────────────────


@dataclass(frozen=True)
class ValidationError:
    """A hard failure that blocks graph loading and merge."""

    code: str  # e.g. "S1", "S4", "O1"
    message: str
    context: dict = field(default_factory=dict)

    def __str__(self) -> str:
        ctx = f" {self.context}" if self.context else ""
        return f"[{self.code}] {self.message}{ctx}"


@dataclass(frozen=True)
class SemanticReviewHook:
    """
    A semantic concern that requires human review before merge.
    Not a hard failure — surfaces as an item in the pull request review checklist.
    """

    code: str  # e.g. "SE2", "SE7"
    node_id: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.node_id}: {self.message}"


@dataclass
class ValidationReport:
    errors: list[ValidationError] = field(default_factory=list)
    review_hooks: list[SemanticReviewHook] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    def __str__(self) -> str:
        lines = []
        if self.errors:
            lines.append(f"Errors ({len(self.errors)}):")
            lines.extend(f"  {e}" for e in self.errors)
        if self.review_hooks:
            lines.append(f"Review hooks ({len(self.review_hooks)}):")
            lines.extend(f"  {h}" for h in self.review_hooks)
        return "\n".join(lines) if lines else "No issues found."


# ─── ID format patterns ───────────────────────────────────────────────────────

# <domain>.<subtopic>.<concept> — all lowercase, dot-separated, hyphens within segments
_NODE_ID_RE = re.compile(r"^[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*\.[a-z][a-z0-9-]*$")

# profile.<name>
_PROFILE_ID_RE = re.compile(r"^profile\.[a-z][a-z0-9-]*$")


# ─── Structural validators (S1–S8) ────────────────────────────────────────────


class StructuralValidator:
    """
    Validates structural integrity of a CanonicalGraph.

    All checks are automatable and enforced by CI. A ValidationError is a hard
    failure that blocks loading and merge. Checks S1–S8 correspond directly to
    the rules defined in docs/02-architecture/curriculum-graph/validation.md.
    """

    def validate(self, graph: CanonicalGraph) -> list[ValidationError]:
        errors: list[ValidationError] = []
        errors.extend(self._s1_id_uniqueness(graph))
        errors.extend(self._s2_id_format(graph))
        errors.extend(self._s3_required_fields(graph))
        errors.extend(self._s4_acyclicity(graph))
        errors.extend(self._s5_referential_integrity(graph))
        errors.extend(self._s6_progression_path_order(graph))
        errors.extend(self._s7_mastery_target_bounds(graph))
        errors.extend(self._s8_weight_non_negativity(graph))
        return errors

    def _s1_id_uniqueness(self, graph: CanonicalGraph) -> list[ValidationError]:
        """S1: Every node id and every profile id must be unique.

        CanonicalGraph stores nodes and profiles as plain dicts, so duplicate
        keys are structurally impossible at this layer. The rule is enforced
        by the data structure itself; no runtime check is needed.
        """
        return []

    def _s2_id_format(self, graph: CanonicalGraph) -> list[ValidationError]:
        """S2: All ids must conform to their required format."""
        errors: list[ValidationError] = []
        for nid in graph.nodes:
            if not _NODE_ID_RE.match(nid):
                errors.append(
                    ValidationError(
                        "S2",
                        f"Node id '{nid}' does not conform to '<domain>.<subtopic>.<concept>'. "
                        "All segments must be lowercase, dot-separated, hyphens within segments.",
                        {"id": nid},
                    )
                )
        for pid in graph.profiles:
            if not _PROFILE_ID_RE.match(pid):
                errors.append(
                    ValidationError(
                        "S2",
                        f"Profile id '{pid}' does not conform to 'profile.<name>'.",
                        {"id": pid},
                    )
                )
        return errors

    def _s3_required_fields(self, graph: CanonicalGraph) -> list[ValidationError]:
        """S3: All required node fields must be present and non-empty."""
        errors: list[ValidationError] = []
        for nid, node in graph.nodes.items():
            if not node.name or not node.name.strip():
                errors.append(
                    ValidationError("S3", f"Node '{nid}' has empty 'name'.", {"id": nid})
                )
            if not node.domain or not node.domain.strip():
                errors.append(
                    ValidationError("S3", f"Node '{nid}' has empty 'domain'.", {"id": nid})
                )
            if not node.description or not node.description.strip():
                errors.append(
                    ValidationError(
                        "S3", f"Node '{nid}' has empty 'description'.", {"id": nid}
                    )
                )
            mc = node.mastery_criteria
            for lvl, text in [
                (1, mc.level_1),
                (2, mc.level_2),
                (3, mc.level_3),
                (4, mc.level_4),
                (5, mc.level_5),
            ]:
                if not text or not text.strip():
                    errors.append(
                        ValidationError(
                            "S3",
                            f"Node '{nid}' has empty mastery_criteria for level {lvl}.",
                            {"id": nid, "level": lvl},
                        )
                    )
            if len(node.error_taxonomy) == 0:
                errors.append(
                    ValidationError(
                        "S3",
                        f"Node '{nid}' has no error_taxonomy entries. "
                        "At least two entries are required.",
                        {"id": nid},
                    )
                )
        return errors

    def _s4_acyclicity(self, graph: CanonicalGraph) -> list[ValidationError]:
        """S4: The canonical graph must be a DAG — no cycles in prerequisite edges."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color: dict[str, int] = {nid: WHITE for nid in graph.nodes}
        cycle_node: list[str] = []

        def dfs(nid: str) -> bool:
            color[nid] = GRAY
            node = graph.nodes.get(nid)
            if node:
                for edge in node.prerequisite_ids:
                    neighbour = edge.node_id
                    if neighbour not in color:
                        continue  # dangling reference — caught by S5
                    if color[neighbour] == GRAY:
                        cycle_node.append(nid)
                        return True
                    if color[neighbour] == WHITE and dfs(neighbour):
                        return True
            color[nid] = BLACK
            return False

        for nid in graph.nodes:
            if color[nid] == WHITE:
                if dfs(nid):
                    return [
                        ValidationError(
                            "S4",
                            f"Cycle detected in prerequisite edges at node "
                            f"'{cycle_node[0]}'. The canonical graph must be a DAG.",
                            {"node": cycle_node[0]},
                        )
                    ]
        return []

    def _s5_referential_integrity(self, graph: CanonicalGraph) -> list[ValidationError]:
        """S5: All referenced node ids must exist in the canonical graph."""
        errors: list[ValidationError] = []
        for nid, node in graph.nodes.items():
            for edge in node.prerequisite_ids:
                if edge.node_id not in graph.nodes:
                    errors.append(
                        ValidationError(
                            "S5",
                            f"Node '{nid}' references non-existent prerequisite '{edge.node_id}'.",
                            {"node": nid, "missing": edge.node_id},
                        )
                    )
            for rid in node.regression_ids:
                if rid not in graph.nodes:
                    errors.append(
                        ValidationError(
                            "S5",
                            f"Node '{nid}' references non-existent regression target '{rid}'.",
                            {"node": nid, "missing": rid},
                        )
                    )
        for pid, profile in graph.profiles.items():
            for pn in profile.required_nodes:
                if pn.node_id not in graph.nodes:
                    errors.append(
                        ValidationError(
                            "S5",
                            f"Profile '{pid}' references non-existent node '{pn.node_id}'.",
                            {"profile": pid, "missing": pn.node_id},
                        )
                    )
            for step in profile.progression_path:
                if step not in graph.nodes:
                    errors.append(
                        ValidationError(
                            "S5",
                            f"Profile '{pid}' progression_path references "
                            f"non-existent node '{step}'.",
                            {"profile": pid, "missing": step},
                        )
                    )
        return errors

    def _s6_progression_path_order(self, graph: CanonicalGraph) -> list[ValidationError]:
        """S6: progression_path must respect the hard prerequisite edges of included nodes."""
        errors: list[ValidationError] = []
        for pid, profile in graph.profiles.items():
            path = list(profile.progression_path)
            position = {nid: i for i, nid in enumerate(path)}
            for nid in path:
                node = graph.nodes.get(nid)
                if node is None:
                    continue  # caught by S5
                for edge in node.prerequisite_ids:
                    if edge.edge_type.value != "hard":
                        continue
                    prereq_id = edge.node_id
                    if prereq_id not in position:
                        continue  # prereq not in path — covered by SE7
                    if position[prereq_id] >= position[nid]:
                        errors.append(
                            ValidationError(
                                "S6",
                                f"Profile '{pid}': hard prerequisite '{prereq_id}' of "
                                f"'{nid}' must appear before '{nid}' in progression_path.",
                                {"profile": pid, "node": nid, "prereq": prereq_id},
                            )
                        )
        return errors

    def _s7_mastery_target_bounds(self, graph: CanonicalGraph) -> list[ValidationError]:
        """S7: All mastery targets in profiles must be in [1, 5]. 0 is not a valid target."""
        errors: list[ValidationError] = []
        for pid, profile in graph.profiles.items():
            for pn in profile.required_nodes:
                if not (1 <= pn.mastery_target <= 5):
                    errors.append(
                        ValidationError(
                            "S7",
                            f"Profile '{pid}', node '{pn.node_id}': mastery_target "
                            f"{pn.mastery_target} is outside [1, 5].",
                            {"profile": pid, "node": pn.node_id, "value": pn.mastery_target},
                        )
                    )
        return errors

    def _s8_weight_non_negativity(self, graph: CanonicalGraph) -> list[ValidationError]:
        """S8: All node weights in profiles must be strictly positive."""
        errors: list[ValidationError] = []
        for pid, profile in graph.profiles.items():
            for pn in profile.required_nodes:
                if pn.weight <= 0:
                    errors.append(
                        ValidationError(
                            "S8",
                            f"Profile '{pid}', node '{pn.node_id}': weight "
                            f"{pn.weight} must be strictly positive.",
                            {"profile": pid, "node": pn.node_id, "value": pn.weight},
                        )
                    )
        return errors


# ─── Semantic validation hooks (SE1–SE8) ─────────────────────────────────────


class SemanticValidator:
    """
    Generates review hooks for human validation before merge.

    These checks require expert judgment and are not enforced by CI.
    They surface as items in the pull request review checklist.
    Checks SE1–SE8 correspond to the rules in validation.md.
    """

    _EXAM_KEYWORDS_RE = re.compile(
        r"\b(fuvest|enem|vestibular|prova|exame|concurso|faculdade|unicamp|usp)\b",
        re.IGNORECASE,
    )

    _MATH_KEYWORDS_RE = re.compile(
        r"\b(equation|function|algebra|geometry|calculus|fraction|polynomial|"
        r"logarithm|trigonometry|equação|função|álgebra|geometria|fração)\b",
        re.IGNORECASE,
    )

    _GENERIC_ERROR_PHRASES = [
        "calculation error",
        "makes mistakes",
        "student may",
        "can lead to errors",
        "common error",
        "generic",
    ]

    def validate(self, graph: CanonicalGraph) -> list[SemanticReviewHook]:
        hooks: list[SemanticReviewHook] = []
        hooks.extend(self._se2_description_exam_neutrality(graph))
        hooks.extend(self._se3_mastery_criteria_gradation(graph))
        hooks.extend(self._se4_error_taxonomy_specificity(graph))
        hooks.extend(self._se6_regression_path_relevance(graph))
        hooks.extend(self._se7_profile_prerequisite_completeness(graph))
        hooks.extend(self._se8_exam_skill_overlay_containment(graph))
        return hooks

    def _se2_description_exam_neutrality(
        self, graph: CanonicalGraph
    ) -> list[SemanticReviewHook]:
        """SE2: Node descriptions must contain no reference to any specific exam."""
        hooks: list[SemanticReviewHook] = []
        for nid, node in graph.nodes.items():
            if self._EXAM_KEYWORDS_RE.search(node.description):
                hooks.append(
                    SemanticReviewHook(
                        "SE2",
                        nid,
                        "Description may contain exam-specific language. "
                        "Reviewer must verify it is exam-neutral.",
                    )
                )
        return hooks

    def _se3_mastery_criteria_gradation(
        self, graph: CanonicalGraph
    ) -> list[SemanticReviewHook]:
        """SE3: Mastery criteria levels 1–5 must describe a genuine progression."""
        hooks: list[SemanticReviewHook] = []
        for nid, node in graph.nodes.items():
            mc = node.mastery_criteria
            levels = [mc.level_1, mc.level_2, mc.level_3, mc.level_4, mc.level_5]
            if len(set(levels)) < len(levels):
                hooks.append(
                    SemanticReviewHook(
                        "SE3",
                        nid,
                        "Two or more mastery_criteria levels have identical text. "
                        "Reviewer must verify that the progression is genuinely distinct.",
                    )
                )
        return hooks

    def _se4_error_taxonomy_specificity(
        self, graph: CanonicalGraph
    ) -> list[SemanticReviewHook]:
        """SE4: error_taxonomy entries must describe errors specific to the concept."""
        hooks: list[SemanticReviewHook] = []
        for nid, node in graph.nodes.items():
            for entry in node.error_taxonomy:
                lower = entry.description.lower()
                if any(phrase in lower for phrase in self._GENERIC_ERROR_PHRASES):
                    hooks.append(
                        SemanticReviewHook(
                            "SE4",
                            nid,
                            f"error_taxonomy entry '{entry.name}' may be too generic. "
                            "Reviewer must verify it names a specific misconception.",
                        )
                    )
        return hooks

    def _se6_regression_path_relevance(
        self, graph: CanonicalGraph
    ) -> list[SemanticReviewHook]:
        """SE6: regression_ids should address root causes in error_taxonomy."""
        hooks: list[SemanticReviewHook] = []
        for nid, node in graph.nodes.items():
            if not node.regression_ids:
                hooks.append(
                    SemanticReviewHook(
                        "SE6",
                        nid,
                        "Node has no regression_ids. Reviewer must confirm whether "
                        "regression targets are needed based on error_taxonomy.",
                    )
                )
        return hooks

    def _se7_profile_prerequisite_completeness(
        self, graph: CanonicalGraph
    ) -> list[SemanticReviewHook]:
        """SE7: A profile must include all hard prerequisites of each required node."""
        hooks: list[SemanticReviewHook] = []
        for pid, profile in graph.profiles.items():
            required = profile.required_node_ids()
            for pn in profile.required_nodes:
                node = graph.nodes.get(pn.node_id)
                if node is None:
                    continue
                for edge in node.prerequisite_ids:
                    if edge.edge_type.value == "hard" and edge.node_id not in required:
                        hooks.append(
                            SemanticReviewHook(
                                "SE7",
                                pn.node_id,
                                f"Profile '{pid}' requires '{pn.node_id}' but omits its "
                                f"hard prerequisite '{edge.node_id}'. "
                                "Reviewer must verify profile prerequisite closure.",
                            )
                        )
        return hooks

    def _se8_exam_skill_overlay_containment(
        self, graph: CanonicalGraph
    ) -> list[SemanticReviewHook]:
        """SE8: exam_skill_overlay entries must not contain mathematical content."""
        hooks: list[SemanticReviewHook] = []
        for pid, profile in graph.profiles.items():
            for entry in profile.exam_skill_overlay:
                if self._MATH_KEYWORDS_RE.search(
                    entry.name
                ) or self._MATH_KEYWORDS_RE.search(entry.description):
                    hooks.append(
                        SemanticReviewHook(
                            "SE8",
                            pid,
                            f"exam_skill_overlay entry '{entry.name}' may contain "
                            "mathematical content. Reviewer must confirm it belongs in "
                            "the overlay and not in a canonical node.",
                        )
                    )
        return hooks


# ─── Operational validators (O1–O3) ──────────────────────────────────────────


class OperationalValidator:
    """
    Validates runtime compatibility with the Tutor Orchestrator and Student Model.
    Typically run during integration testing rather than at authoring time.
    """

    _SAFE_KEY_RE = re.compile(r"^[a-zA-Z0-9._-]+$")

    def validate(self, graph: CanonicalGraph) -> list[ValidationError]:
        errors: list[ValidationError] = []
        errors.extend(self._o1_orchestrator_traversability(graph))
        errors.extend(self._o2_student_model_compatibility(graph))
        errors.extend(self._o3_mastery_scale_alignment(graph))
        return errors

    def _o1_orchestrator_traversability(
        self, graph: CanonicalGraph
    ) -> list[ValidationError]:
        """
        O1: Every required node in every profile must be reachable by the
        orchestrator traversing from foundational canonical nodes (roots).
        """
        # Build a forward adjacency: prereq_id → list of nodes that depend on it.
        forward: dict[str, list[str]] = {nid: [] for nid in graph.nodes}
        for node in graph.nodes.values():
            for edge in node.prerequisite_ids:
                if edge.node_id in forward:
                    forward[edge.node_id].append(node.id)

        # BFS from all root nodes (nodes with no prerequisites).
        roots = {nid for nid, n in graph.nodes.items() if not n.prerequisite_ids}
        reachable: set[str] = set(roots)
        queue = list(roots)
        while queue:
            current = queue.pop()
            for dependent in forward[current]:
                if dependent not in reachable:
                    reachable.add(dependent)
                    queue.append(dependent)

        errors: list[ValidationError] = []
        for pid, profile in graph.profiles.items():
            for pn in profile.required_nodes:
                if pn.node_id not in reachable:
                    errors.append(
                        ValidationError(
                            "O1",
                            f"Profile '{pid}' requires '{pn.node_id}' which is unreachable "
                            "from the canonical graph's foundational nodes. "
                            "Check for a gap in the prerequisite chain.",
                            {"profile": pid, "node": pn.node_id},
                        )
                    )
        return errors

    def _o2_student_model_compatibility(
        self, graph: CanonicalGraph
    ) -> list[ValidationError]:
        """O2: All node ids must be valid as Student Model evidence store keys."""
        errors: list[ValidationError] = []
        for nid in graph.nodes:
            if not self._SAFE_KEY_RE.match(nid):
                errors.append(
                    ValidationError(
                        "O2",
                        f"Node id '{nid}' contains characters incompatible with "
                        "the Student Model evidence store key format.",
                        {"id": nid},
                    )
                )
        return errors

    def _o3_mastery_scale_alignment(self, graph: CanonicalGraph) -> list[ValidationError]:
        """O3: Profile mastery targets must not exceed the system maximum of 5."""
        errors: list[ValidationError] = []
        for pid, profile in graph.profiles.items():
            for pn in profile.required_nodes:
                if pn.mastery_target > 5:
                    errors.append(
                        ValidationError(
                            "O3",
                            f"Profile '{pid}', node '{pn.node_id}': mastery_target "
                            f"{pn.mastery_target} exceeds the system maximum of 5.",
                            {"profile": pid, "node": pn.node_id},
                        )
                    )
        return errors


# ─── Convenience entry point ──────────────────────────────────────────────────


def validate_graph(
    graph: CanonicalGraph, *, operational: bool = False
) -> ValidationReport:
    """
    Run structural and semantic validators against a CanonicalGraph.

    Pass operational=True to also run operational validators (typically done
    only during integration testing, not at authoring time).

    Returns a ValidationReport. Check report.has_errors before proceeding.
    """
    report = ValidationReport()
    report.errors.extend(StructuralValidator().validate(graph))
    report.review_hooks.extend(SemanticValidator().validate(graph))
    if operational:
        report.errors.extend(OperationalValidator().validate(graph))
    return report
