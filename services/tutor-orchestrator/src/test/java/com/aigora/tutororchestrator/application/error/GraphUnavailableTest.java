package com.aigora.tutororchestrator.application.error;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class GraphUnavailableTest {

    @Test
    void shouldReturnGraphUnavailableCode() {
        var error = new GraphUnavailable();

        assertEquals(
                ApplicationErrorCode.GRAPH_UNAVAILABLE,
                error.code()
        );
    }

    @Test
    void shouldUseDefaultMessage() {
        var error = new GraphUnavailable();

        assertEquals(
                "Curriculum Graph is currently unavailable",
                error.message()
        );
    }

    @Test
    void shouldUseCustomMessage() {
        var error = new GraphUnavailable(
                "Curriculum Graph cannot be reached"
        );

        assertEquals(
                "Curriculum Graph cannot be reached",
                error.message()
        );
    }

    @Test
    void shouldTrimCustomMessage() {
        var error = new GraphUnavailable(
                "  Curriculum Graph cannot be reached  "
        );

        assertEquals(
                "Curriculum Graph cannot be reached",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultMessageWhenMessageIsNull() {
        var error = new GraphUnavailable(null);

        assertEquals(
                "Curriculum Graph is currently unavailable",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultMessageWhenMessageIsBlank() {
        var error = new GraphUnavailable("   ");

        assertEquals(
                "Curriculum Graph is currently unavailable",
                error.message()
        );
    }

    @Test
    void shouldCompareByValue() {
        var first = new GraphUnavailable("Graph unavailable");
        var second = new GraphUnavailable("Graph unavailable");

        assertEquals(first, second);
    }
}