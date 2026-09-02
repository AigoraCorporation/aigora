package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.valueobjects.*;
import java.time.Instant;
public record ExerciseCompleted(EventId eventId, LearningSessionId sessionId, SessionVersion sessionVersion, CorrelationId correlationId, CausationId causationId, Instant occurredAt, ExerciseAttemptId attemptId, ExerciseId exerciseId) implements SessionEvent {    public ExerciseCompleted {
        SessionEventValidation.required(eventId, sessionId, sessionVersion, correlationId, causationId, occurredAt);
    }
}
