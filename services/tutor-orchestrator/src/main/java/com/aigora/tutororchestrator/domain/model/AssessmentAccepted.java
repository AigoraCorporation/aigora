package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.valueobjects.*;
import java.time.Instant;
public record AssessmentAccepted(EventId eventId, LearningSessionId sessionId, SessionVersion sessionVersion, CorrelationId correlationId, CausationId causationId, Instant occurredAt, ExerciseAttemptId attemptId, AssessmentResultId assessmentResultId) implements SessionEvent {    public AssessmentAccepted {
        SessionEventValidation.required(eventId, sessionId, sessionVersion, correlationId, causationId, occurredAt);
    }
}
