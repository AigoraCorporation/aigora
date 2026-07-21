package com.aigora.tutororchestrator.domain.model;

import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.DecisionId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class OrchestrationDecisionTest {

    @Test
    void shouldCreateSelectedOrchestrationDecision() {
        OrchestrationDecision decision = new OrchestrationDecision(
                new DecisionId("decision-001"),
                new StudentId("student-001"),
                new NodeId("node-001"),
                DecisionStatus.SELECTED,
                new DecisionReason("SELECTED", "Candidate selected successfully"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("corr-001")
        );

        assertEquals(new DecisionId("decision-001"), decision.decisionId());
        assertEquals(new StudentId("student-001"), decision.studentId());
        assertEquals(new NodeId("node-001"), decision.selectedNodeId());
        assertEquals(DecisionStatus.SELECTED, decision.status());
        assertEquals(new DecisionReason("SELECTED", "Candidate selected successfully"), decision.reason());
        assertEquals(new GraphVersion("v1.0.0"), decision.graphVersion());
        assertEquals(new CorrelationId("corr-001"), decision.correlationId());
    }

    @Test
    void shouldCreateNoCandidateAvailableDecisionWithoutSelectedNode() {
        OrchestrationDecision decision = new OrchestrationDecision(
                new DecisionId("decision-001"),
                new StudentId("student-001"),
                null,
                DecisionStatus.NO_CANDIDATE_AVAILABLE,
                new DecisionReason("NO_CANDIDATE_AVAILABLE", "No valid candidate was available"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("corr-001")
        );

        assertNull(decision.selectedNodeId());
        assertEquals(DecisionStatus.NO_CANDIDATE_AVAILABLE, decision.status());
    }

    @Test
    void shouldRejectSelectedDecisionWithoutSelectedNode() {
        assertThrows(IllegalArgumentException.class, () ->
                new OrchestrationDecision(
                        new DecisionId("decision-001"),
                        new StudentId("student-001"),
                        null,
                        DecisionStatus.SELECTED,
                        new DecisionReason("SELECTED", "Candidate selected successfully"),
                        new GraphVersion("v1.0.0"),
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullDecisionId() {
        assertThrows(IllegalArgumentException.class, () ->
                new OrchestrationDecision(
                        null,
                        new StudentId("student-001"),
                        new NodeId("node-001"),
                        DecisionStatus.SELECTED,
                        new DecisionReason("SELECTED", "Candidate selected successfully"),
                        new GraphVersion("v1.0.0"),
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullStudentId() {
        assertThrows(IllegalArgumentException.class, () ->
                new OrchestrationDecision(
                        new DecisionId("decision-001"),
                        null,
                        new NodeId("node-001"),
                        DecisionStatus.SELECTED,
                        new DecisionReason("SELECTED", "Candidate selected successfully"),
                        new GraphVersion("v1.0.0"),
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullStatus() {
        assertThrows(IllegalArgumentException.class, () ->
                new OrchestrationDecision(
                        new DecisionId("decision-001"),
                        new StudentId("student-001"),
                        new NodeId("node-001"),
                        null,
                        new DecisionReason("SELECTED", "Candidate selected successfully"),
                        new GraphVersion("v1.0.0"),
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullReason() {
        assertThrows(IllegalArgumentException.class, () ->
                new OrchestrationDecision(
                        new DecisionId("decision-001"),
                        new StudentId("student-001"),
                        new NodeId("node-001"),
                        DecisionStatus.SELECTED,
                        null,
                        new GraphVersion("v1.0.0"),
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullGraphVersion() {
        assertThrows(IllegalArgumentException.class, () ->
                new OrchestrationDecision(
                        new DecisionId("decision-001"),
                        new StudentId("student-001"),
                        new NodeId("node-001"),
                        DecisionStatus.SELECTED,
                        new DecisionReason("SELECTED", "Candidate selected successfully"),
                        null,
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullCorrelationId() {
        assertThrows(IllegalArgumentException.class, () ->
                new OrchestrationDecision(
                        new DecisionId("decision-001"),
                        new StudentId("student-001"),
                        new NodeId("node-001"),
                        DecisionStatus.SELECTED,
                        new DecisionReason("SELECTED", "Candidate selected successfully"),
                        new GraphVersion("v1.0.0"),
                        null
                )
        );
    }
}