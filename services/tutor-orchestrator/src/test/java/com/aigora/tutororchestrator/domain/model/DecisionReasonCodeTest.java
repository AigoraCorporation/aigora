package com.aigora.tutororchestrator.domain.model;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class DecisionReasonCodeTest {

    @Test
    void shouldExposeStableSerializedValue() {
        assertEquals(
                "LEARNING_COMPLETED",
                DecisionReasonCode.LEARNING_COMPLETED.value()
        );
    }

    @Test
    void shouldCreateDecisionReasonFromReasonCode() {
        var reason = new DecisionReason(
                DecisionReasonCode.CANDIDATE_SELECTED,
                "Candidate selected"
        );

        assertEquals("CANDIDATE_SELECTED", reason.code());
        assertEquals("Candidate selected", reason.description());
    }
}