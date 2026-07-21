package com.aigora.tutororchestrator.testsupport.assertion;

import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;

import static org.junit.jupiter.api.Assertions.*;

public final class DecisionAssertions {

    private DecisionAssertions() {
    }

    public static void assertSelectedNode(
            OrchestrationDecision decision,
            String expectedNodeId
    ) {
        assertEquals(DecisionStatus.SELECTED, decision.status());
        assertEquals(new NodeId(expectedNodeId), decision.selectedNodeId());
        assertNotNull(decision.decisionId());
        assertNotNull(decision.reason());
    }

    public static void assertNoCandidateAvailable(OrchestrationDecision decision) {
        assertEquals(DecisionStatus.NO_CANDIDATE_AVAILABLE, decision.status());
        assertNull(decision.selectedNodeId());
        assertNotNull(decision.decisionId());
        assertNotNull(decision.reason());
        assertEquals("NO_CANDIDATE_AVAILABLE", decision.reason().code());
    }
}