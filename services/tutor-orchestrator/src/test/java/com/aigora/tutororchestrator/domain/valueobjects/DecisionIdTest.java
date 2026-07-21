package com.aigora.tutororchestrator.domain.valueobjects;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class DecisionIdTest {

    @Test
    void shouldCreateDecisionId() {
        DecisionId decisionId = new DecisionId("decision-001");

        assertEquals("decision-001", decisionId.value());
    }

    @Test
    void shouldCompareByValue() {
        DecisionId first = new DecisionId("decision-001");
        DecisionId second = new DecisionId("decision-001");

        assertEquals(first, second);
    }

    @Test
    void shouldGenerateDecisionId() {
        DecisionId decisionId = DecisionId.generate();

        assertNotNull(decisionId);
        assertNotNull(decisionId.value());
        assertFalse(decisionId.value().isBlank());
    }

    @Test
    void shouldRejectBlankValue() {
        assertThrows(IllegalArgumentException.class, () -> new DecisionId(""));
    }

    @Test
    void shouldRejectNullValue() {
        assertThrows(IllegalArgumentException.class, () -> new DecisionId(null));
    }

    @Test
    void shouldGenerateDifferentIds() {
        var first = DecisionId.generate();
        var second = DecisionId.generate();

        assertNotEquals(first, second);
    }
}