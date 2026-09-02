package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.valueobjects.*;
import java.time.Instant;
public sealed interface SessionEvent permits LearningSessionStarted, ExerciseCompleted, AssessmentAccepted, NextNodeApplied, LearningSessionCompleted, LearningContinued, LearningSessionInterrupted, LearningSessionFailed {
    EventId eventId(); LearningSessionId sessionId(); SessionVersion sessionVersion(); CorrelationId correlationId(); CausationId causationId(); Instant occurredAt();
    default String schemaVersion(){ return "1"; }
}
