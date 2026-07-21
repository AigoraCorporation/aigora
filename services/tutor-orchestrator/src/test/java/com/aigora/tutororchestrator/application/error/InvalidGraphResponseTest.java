package com.aigora.tutororchestrator.application.error;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class InvalidGraphResponseTest {

    @Test
    void shouldReturnInvalidGraphResponseCode() {
        var error = new InvalidGraphResponse();

        assertEquals(
                ApplicationErrorCode.INVALID_GRAPH_RESPONSE,
                error.code()
        );
    }

    @Test
    void shouldUseDefaultMessage() {
        var error = new InvalidGraphResponse();

        assertEquals(
                "Curriculum Graph returned an invalid response",
                error.message()
        );
    }

    @Test
    void shouldUseCustomMessage() {
        var error = new InvalidGraphResponse(
                "Graph response does not contain a version"
        );

        assertEquals(
                "Graph response does not contain a version",
                error.message()
        );
    }

    @Test
    void shouldTrimCustomMessage() {
        var error = new InvalidGraphResponse(
                "  Invalid graph payload  "
        );

        assertEquals(
                "Invalid graph payload",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultMessageWhenMessageIsNull() {
        var error = new InvalidGraphResponse(null);

        assertEquals(
                "Curriculum Graph returned an invalid response",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultMessageWhenMessageIsBlank() {
        var error = new InvalidGraphResponse("");

        assertEquals(
                "Curriculum Graph returned an invalid response",
                error.message()
        );
    }

    @Test
    void shouldCompareByValue() {
        var first = new InvalidGraphResponse("Invalid graph payload");
        var second = new InvalidGraphResponse("Invalid graph payload");

        assertEquals(first, second);
    }
}