package com.aigora.tutororchestrator.domain.model;

import com.aigora.tutororchestrator.domain.valueobjects.*;
import org.junit.jupiter.api.Test;

import java.time.Instant;

import static org.junit.jupiter.api.Assertions.*;

class SessionEventContractTest {
    @Test
    void shouldExposeStableSchemaVersionAndRequiredMetadata() {
        SessionEvent event = new LearningSessionStarted(
                new EventId("event-1"), new LearningSessionId("s1"), new SessionVersion(1), new CorrelationId("c1"), new CausationId("root"), Instant.EPOCH, new NodeId("n1"), new ExerciseId("e1")
        );
        assertEquals("1", event.schemaVersion());
        assertEquals(new LearningSessionId("s1"), event.sessionId());
        assertEquals(new SessionVersion(1), event.sessionVersion());
    }

    @Test
    void shouldRejectNullEventMetadata() {
        assertThrows(IllegalArgumentException.class, () -> new LearningSessionStarted(
                null, new LearningSessionId("s1"), new SessionVersion(1), new CorrelationId("c1"), new CausationId("root"), Instant.EPOCH, new NodeId("n1"), new ExerciseId("e1")
        ));
    }
}
