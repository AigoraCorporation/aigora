package com.aigora.tutororchestrator.domain.model;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class DecisionReasonTest {

    @Test
    void shouldCreateDecisionReason() {
        DecisionReason reason = new DecisionReason(
                "ELIGIBLE_CANDIDATE_SELECTED",
                "Candidate passed eligibility and ranking"
        );

        assertEquals("ELIGIBLE_CANDIDATE_SELECTED", reason.code());
        assertEquals("Candidate passed eligibility and ranking", reason.description());
    }

    @Test
    void shouldCompareByValue() {
        DecisionReason first = new DecisionReason("CODE", "Description");
        DecisionReason second = new DecisionReason("CODE", "Description");

        assertEquals(first, second);
    }

    @Test
    void shouldRejectNullCode() {
        assertThrows(IllegalArgumentException.class, () ->
                new DecisionReason((DecisionReasonCode)null, "Description")
        );
    }

    @Test
    void shouldRejectBlankCode() {
        assertThrows(IllegalArgumentException.class, () ->
                new DecisionReason("", "Description")
        );
    }

    @Test
    void shouldRejectNullDescription() {
        assertThrows(IllegalArgumentException.class, () ->
                new DecisionReason("CODE", null)
        );
    }

    @Test
    void shouldRejectBlankDescription() {
        assertThrows(IllegalArgumentException.class, () ->
                new DecisionReason("CODE", "")
        );
    }
}