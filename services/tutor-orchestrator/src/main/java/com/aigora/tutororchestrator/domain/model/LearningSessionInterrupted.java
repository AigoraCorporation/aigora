package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.valueobjects.*;
import java.time.Instant;
public record LearningSessionInterrupted(EventId eventId, LearningSessionId sessionId, SessionVersion sessionVersion, CorrelationId correlationId, CausationId causationId, Instant occurredAt, String reason) implements SessionEvent {    public LearningSessionInterrupted {
        SessionEventValidation.required(eventId, sessionId, sessionVersion, correlationId, causationId, occurredAt);
    }
}
