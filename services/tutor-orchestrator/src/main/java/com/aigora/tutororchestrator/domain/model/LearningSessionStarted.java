package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.valueobjects.*;
import java.time.Instant;
public record LearningSessionStarted(EventId eventId, LearningSessionId sessionId, SessionVersion sessionVersion, CorrelationId correlationId, CausationId causationId, Instant occurredAt, NodeId nodeId, ExerciseId exerciseId) implements SessionEvent {    public LearningSessionStarted {
        SessionEventValidation.required(eventId, sessionId, sessionVersion, correlationId, causationId, occurredAt);
    }
}
