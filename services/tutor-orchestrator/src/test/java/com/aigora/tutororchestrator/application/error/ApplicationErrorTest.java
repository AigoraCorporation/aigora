package com.aigora.tutororchestrator.application.error;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;

class ApplicationErrorTest {

    @Test
    void shouldExposeErrorsThroughApplicationErrorContract() {
        ApplicationError error = new GraphUnavailable();

        assertInstanceOf(GraphUnavailable.class, error);
        assertEquals(
                ApplicationErrorCode.GRAPH_UNAVAILABLE,
                error.code()
        );
        assertEquals(
                "Curriculum Graph is currently unavailable",
                error.message()
        );
    }
}