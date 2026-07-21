package com.aigora.tutororchestrator.application.error;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class AssessmentUnavailableTest {

    @Test
    void shouldReturnAssessmentUnavailableCode() {
        var error = new AssessmentUnavailable();

        assertEquals(
                ApplicationErrorCode.ASSESSMENT_UNAVAILABLE,
                error.code()
        );
    }

    @Test
    void shouldUseDefaultMessage() {
        var error = new AssessmentUnavailable();

        assertEquals(
                "Assessment service is currently unavailable",
                error.message()
        );
    }

    @Test
    void shouldUseCustomMessage() {
        var error = new AssessmentUnavailable(
                "Assessment service could not be reached"
        );

        assertEquals(
                "Assessment service could not be reached",
                error.message()
        );
    }

    @Test
    void shouldTrimCustomMessage() {
        var error = new AssessmentUnavailable(
                "  Assessment service could not be reached  "
        );

        assertEquals(
                "Assessment service could not be reached",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultMessageWhenMessageIsNull() {
        var error = new AssessmentUnavailable(null);

        assertEquals(
                "Assessment service is currently unavailable",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultMessageWhenMessageIsBlank() {
        var error = new AssessmentUnavailable("");

        assertEquals(
                "Assessment service is currently unavailable",
                error.message()
        );
    }

    @Test
    void shouldCompareByValue() {
        var first = new AssessmentUnavailable("Assessment unavailable");
        var second = new AssessmentUnavailable("Assessment unavailable");

        assertEquals(first, second);
    }
}