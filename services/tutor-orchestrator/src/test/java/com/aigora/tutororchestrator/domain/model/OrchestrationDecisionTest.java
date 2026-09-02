package com.aigora.tutororchestrator.domain.model;

import com.aigora.tutororchestrator.domain.valueobjects.DecisionId;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import static com.aigora.tutororchestrator.testsupport.builder.DecisionTraceBuilder.aDecisionTrace;
import static org.junit.jupiter.api.Assertions.*;

class OrchestrationDecisionTest {

    @Test
    void shouldCreateSelectedOrchestrationDecision() {
        var trace = aDecisionTrace().build();
        var decision = new OrchestrationDecision(
                new DecisionId("decision-001"),
                new StudentId("student-001"),
                new NodeId("node-001"),
                DecisionStatus.SELECTED,
                new DecisionReason("SELECTED", "Candidate selected successfully"),
                trace
        );

        assertEquals(new DecisionId("decision-001"), decision.decisionId());
        assertEquals(new StudentId("student-001"), decision.studentId());
        assertEquals(new NodeId("node-001"), decision.selectedNodeId());
        assertEquals(DecisionStatus.SELECTED, decision.status());
        assertEquals(trace, decision.trace());
    }

    @Test
    void shouldCreateNoCandidateAvailableDecisionWithoutSelectedNode() {
        var decision = new OrchestrationDecision(
                new DecisionId("decision-001"), new StudentId("student-001"), null,
                DecisionStatus.NO_CANDIDATE_AVAILABLE,
                new DecisionReason("NO_CANDIDATE_AVAILABLE", "No valid candidate was available"),
                aDecisionTrace().build()
        );
        assertNull(decision.selectedNodeId());
        assertEquals(DecisionStatus.NO_CANDIDATE_AVAILABLE, decision.status());
    }

    @Test
    void shouldRejectSelectedDecisionWithoutSelectedNode() {
        assertThrows(IllegalArgumentException.class, () -> new OrchestrationDecision(
                new DecisionId("decision-001"), new StudentId("student-001"), null,
                DecisionStatus.SELECTED, new DecisionReason("SELECTED", "Candidate selected successfully"),
                aDecisionTrace().build()));
    }

    @Test void shouldRejectNullDecisionId() {
        assertThrows(IllegalArgumentException.class, () -> new OrchestrationDecision(
                null, new StudentId("student-001"), new NodeId("node-001"), DecisionStatus.SELECTED,
                new DecisionReason("SELECTED", "Candidate selected successfully"), aDecisionTrace().build()));
    }

    @Test void shouldRejectNullStudentId() {
        assertThrows(IllegalArgumentException.class, () -> new OrchestrationDecision(
                new DecisionId("decision-001"), null, new NodeId("node-001"), DecisionStatus.SELECTED,
                new DecisionReason("SELECTED", "Candidate selected successfully"), aDecisionTrace().build()));
    }

    @Test void shouldRejectNullStatus() {
        assertThrows(IllegalArgumentException.class, () -> new OrchestrationDecision(
                new DecisionId("decision-001"), new StudentId("student-001"), new NodeId("node-001"), null,
                new DecisionReason("SELECTED", "Candidate selected successfully"), aDecisionTrace().build()));
    }

    @Test void shouldRejectNullReason() {
        assertThrows(IllegalArgumentException.class, () -> new OrchestrationDecision(
                new DecisionId("decision-001"), new StudentId("student-001"), new NodeId("node-001"),
                DecisionStatus.SELECTED, null, aDecisionTrace().build()));
    }

    @Test void shouldRejectNullTrace() {
        assertThrows(IllegalArgumentException.class, () -> new OrchestrationDecision(
                new DecisionId("decision-001"), new StudentId("student-001"), new NodeId("node-001"),
                DecisionStatus.SELECTED, new DecisionReason("SELECTED", "Candidate selected successfully"), null));
    }
}
