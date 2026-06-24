package com.aigora.tutororchestrator.domain.valueobjects;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class GraphVersionTest {

    @Test
    void shouldCreateGraphVersion() {
        GraphVersion version = new GraphVersion("v1.0.0");

        assertEquals("v1.0.0", version.value());
    }

    @Test
    void shouldCompareByValue() {
        GraphVersion first = new GraphVersion("v1.0.0");
        GraphVersion second = new GraphVersion("v1.0.0");

        assertEquals(first, second);
    }

    @Test
    void shouldRejectBlankValue() {
        assertThrows(IllegalArgumentException.class, () -> new GraphVersion(""));
    }

    @Test
    void shouldRejectNullValue() {
        assertThrows(IllegalArgumentException.class, () -> new GraphVersion(null));
    }
}