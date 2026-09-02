package com.aigora.tutororchestrator.domain.selection;

import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import java.util.List;

import static com.aigora.tutororchestrator.testsupport.builder.DecisionTraceBuilder.aDecisionTrace;
import static org.junit.jupiter.api.Assertions.*;

class DefaultSelectionStrategyTest {

    private final SelectionStrategy selectionStrategy = new DefaultSelectionStrategy();

    @Test
    void shouldSelectFirstRankedCandidate() {
        var trace = aDecisionTrace().build();
        var decision = selectionStrategy.select(
                List.of(candidate("node-001", CandidateClassification.NEXT_LEARNING),
                        candidate("node-002", CandidateClassification.REINFORCEMENT)),
                new StudentId("student-001"), trace);

        assertEquals(DecisionStatus.SELECTED, decision.status());
        assertEquals(new NodeId("node-001"), decision.selectedNodeId());
        assertEquals(trace, decision.trace());
        assertEquals("CANDIDATE_SELECTED", decision.reason().code());
        assertNotNull(decision.decisionId());
    }

    @Test
    void shouldReturnNoCandidateAvailableDecisionWhenCandidateListIsEmpty() {
        var trace = aDecisionTrace().build();
        var decision = selectionStrategy.select(List.of(), new StudentId("student-001"), trace);
        assertEquals(DecisionStatus.NO_CANDIDATE_AVAILABLE, decision.status());
        assertNull(decision.selectedNodeId());
        assertEquals(trace, decision.trace());
        assertEquals("NO_CANDIDATE_AVAILABLE", decision.reason().code());
    }

    @Test
    void shouldBeDeterministicForSameRankedCandidatesExceptGeneratedDecisionId() {
        var candidates = List.of(candidate("node-001", CandidateClassification.NEXT_LEARNING));
        var trace = aDecisionTrace().build();
        var first = selectionStrategy.select(candidates, new StudentId("student-001"), trace);
        var second = selectionStrategy.select(candidates, new StudentId("student-001"), trace);
        assertEquals(first.status(), second.status());
        assertEquals(first.studentId(), second.studentId());
        assertEquals(first.selectedNodeId(), second.selectedNodeId());
        assertEquals(first.reason(), second.reason());
        assertEquals(first.trace(), second.trace());
    }

    @Test
    void shouldRejectNullRankedCandidates() {
        assertThrows(IllegalArgumentException.class, () ->
                selectionStrategy.select(null, new StudentId("student-001"), aDecisionTrace().build()));
    }

    @Test
    void shouldRejectNullStudentId() {
        assertThrows(IllegalArgumentException.class, () ->
                selectionStrategy.select(List.of(candidate("node-001", CandidateClassification.NEXT_LEARNING)),
                        null, aDecisionTrace().build()));
    }

    @Test
    void shouldRejectNullDecisionTrace() {
        assertThrows(IllegalArgumentException.class, () ->
                selectionStrategy.select(List.of(candidate("node-001", CandidateClassification.NEXT_LEARNING)),
                        new StudentId("student-001"), null));
    }

    private LearningCandidate candidate(String nodeId, CandidateClassification classification) {
        return new LearningCandidate(new NodeId(nodeId), classification);
    }
}
