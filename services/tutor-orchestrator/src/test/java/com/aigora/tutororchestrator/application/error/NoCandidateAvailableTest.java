package com.aigora.tutororchestrator.application.error;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class NoCandidateAvailableTest {

    @Test
    void shouldReturnNoCandidateAvailableCode() {
        var error = new NoCandidateAvailable();

        assertEquals(
                ApplicationErrorCode.NO_CANDIDATE_AVAILABLE,
                error.code()
        );
    }

    @Test
    void shouldUseDefaultMessage() {
        var error = new NoCandidateAvailable();

        assertEquals(
                "No valid learning candidate is available",
                error.message()
        );
    }

    @Test
    void shouldUseCustomMessage() {
        var error = new NoCandidateAvailable(
                "No eligible candidate remained after policy execution"
        );

        assertEquals(
                "No eligible candidate remained after policy execution",
                error.message()
        );
    }

    @Test
    void shouldTrimCustomMessage() {
        var error = new NoCandidateAvailable(
                "  No candidate remained  "
        );

        assertEquals(
                "No candidate remained",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultMessageWhenMessageIsNull() {
        var error = new NoCandidateAvailable(null);

        assertEquals(
                "No valid learning candidate is available",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultMessageWhenMessageIsBlank() {
        var error = new NoCandidateAvailable(" ");

        assertEquals(
                "No valid learning candidate is available",
                error.message()
        );
    }

    @Test
    void shouldCompareByValue() {
        var first = new NoCandidateAvailable("No candidate");
        var second = new NoCandidateAvailable("No candidate");

        assertEquals(first, second);
    }
}