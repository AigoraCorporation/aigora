package com.aigora.tutororchestrator.domain.valueobjects;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CorrelationIdTest {

    @Test
    void shouldCreateCorrelationId() {
        CorrelationId correlationId = new CorrelationId("corr-001");

        assertEquals("corr-001", correlationId.value());
    }

    @Test
    void shouldCompareByValue() {
        CorrelationId first = new CorrelationId("corr-001");
        CorrelationId second = new CorrelationId("corr-001");

        assertEquals(first, second);
    }

    @Test
    void shouldGenerateCorrelationId() {
        CorrelationId correlationId = CorrelationId.generate();

        assertNotNull(correlationId);
        assertNotNull(correlationId.value());
        assertFalse(correlationId.value().isBlank());
    }

    @Test
    void shouldRejectBlankValue() {
        assertThrows(IllegalArgumentException.class, () -> new CorrelationId(""));
    }

    @Test
    void shouldRejectNullValue() {
        assertThrows(IllegalArgumentException.class, () -> new CorrelationId(null));
    }

    @Test
    void shouldGenerateDifferentIds() {
        var first = DecisionId.generate();
        var second = DecisionId.generate();

        assertNotEquals(first, second);
    }
}