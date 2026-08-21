package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.valueobjects.*;
import java.time.Instant;
public record LearningSessionCompleted(EventId eventId, LearningSessionId sessionId, SessionVersion sessionVersion, CorrelationId correlationId, CausationId causationId, Instant occurredAt, DecisionId decisionId, String reason) implements SessionEvent {    public LearningSessionCompleted {
        SessionEventValidation.required(eventId, sessionId, sessionVersion, correlationId, causationId, occurredAt);
    }
}
