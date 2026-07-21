package com.aigora.tutororchestrator.domain.valueobjects;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class NodeIdTest {

    @Test
    void shouldCreateNodeId() {
        NodeId nodeId = new NodeId("node-001");

        assertEquals("node-001", nodeId.value());
    }

    @Test
    void shouldCompareByValue() {
        NodeId first = new NodeId("node-001");
        NodeId second = new NodeId("node-001");

        assertEquals(first, second);
    }

    @Test
    void shouldRejectBlankValue() {
        assertThrows(IllegalArgumentException.class, () -> new NodeId(""));
    }

    @Test
    void shouldRejectNullValue() {
        assertThrows(IllegalArgumentException.class, () -> new NodeId(null));
    }
}