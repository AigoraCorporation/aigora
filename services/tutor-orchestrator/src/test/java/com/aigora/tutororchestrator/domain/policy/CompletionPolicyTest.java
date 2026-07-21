package com.aigora.tutororchestrator.domain.policy;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CompletionPolicyTest {

    private final CompletionPolicy policy = new CompletionPolicy();

    @Test
    void shouldReturnCompletedWhenCurrentNodeIsMastered() {
        assertTrue(policy.isCompleted(true));
    }

    @Test
    void shouldReturnNotCompletedWhenCurrentNodeIsNotMastered() {
        assertFalse(policy.isCompleted(false));
    }

    @Test
    void shouldBeDeterministicForSameInput() {
        assertEquals(policy.isCompleted(true), policy.isCompleted(true));
        assertEquals(policy.isCompleted(false), policy.isCompleted(false));
    }
}