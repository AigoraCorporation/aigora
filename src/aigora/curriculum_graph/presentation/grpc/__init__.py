"""gRPC delivery adapter for aigora.curriculum_graph.v1 (ADR-007)."""
from aigora.curriculum_graph.presentation.grpc.servicer import CurriculumGraphServicer, register

__all__ = ["CurriculumGraphServicer", "register"]
