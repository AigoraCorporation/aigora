package com.aigora.tutororchestrator.domain.selection;

import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class DefaultSelectionStrategyTest {

    private final SelectionStrategy selectionStrategy = new DefaultSelectionStrategy();

    @Test
    void shouldSelectFirstRankedCandidate() {
        var decision = selectionStrategy.select(
                List.of(
                        candidate("node-001", CandidateClassification.NEXT_LEARNING),
                        candidate("node-002", CandidateClassification.REINFORCEMENT)
                ),
                new StudentId("student-001"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("corr-001")
        );

        assertEquals(DecisionStatus.SELECTED, decision.status());
        assertEquals(new StudentId("student-001"), decision.studentId());
        assertEquals(new NodeId("node-001"), decision.selectedNodeId());
        assertEquals(new GraphVersion("v1.0.0"), decision.graphVersion());
        assertEquals(new CorrelationId("corr-001"), decision.correlationId());
        assertEquals("CANDIDATE_SELECTED", decision.reason().code());
        assertNotNull(decision.decisionId());
    }

    @Test
    void shouldReturnNoCandidateAvailableDecisionWhenCandidateListIsEmpty() {
        var decision = selectionStrategy.select(
                List.of(),
                new StudentId("student-001"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("corr-001")
        );

        assertEquals(DecisionStatus.NO_CANDIDATE_AVAILABLE, decision.status());
        assertEquals(new StudentId("student-001"), decision.studentId());
        assertNull(decision.selectedNodeId());
        assertEquals(new GraphVersion("v1.0.0"), decision.graphVersion());
        assertEquals(new CorrelationId("corr-001"), decision.correlationId());
        assertEquals("NO_CANDIDATE_AVAILABLE", decision.reason().code());
        assertNotNull(decision.decisionId());
    }

    @Test
    void shouldBeDeterministicForSameRankedCandidatesExceptGeneratedDecisionId() {
        var candidates = List.of(
                candidate("node-001", CandidateClassification.NEXT_LEARNING),
                candidate("node-002", CandidateClassification.REINFORCEMENT)
        );

        var first = selectionStrategy.select(
                candidates,
                new StudentId("student-001"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("corr-001")
        );

        var second = selectionStrategy.select(
                candidates,
                new StudentId("student-001"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("corr-001")
        );

        assertEquals(first.status(), second.status());
        assertEquals(first.studentId(), second.studentId());
        assertEquals(first.selectedNodeId(), second.selectedNodeId());
        assertEquals(first.reason(), second.reason());
        assertEquals(first.graphVersion(), second.graphVersion());
        assertEquals(first.correlationId(), second.correlationId());
    }

    @Test
    void shouldRejectNullRankedCandidates() {
        assertThrows(IllegalArgumentException.class, () ->
                selectionStrategy.select(
                        null,
                        new StudentId("student-001"),
                        new GraphVersion("v1.0.0"),
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullStudentId() {
        assertThrows(IllegalArgumentException.class, () ->
                selectionStrategy.select(
                        List.of(candidate("node-001", CandidateClassification.NEXT_LEARNING)),
                        null,
                        new GraphVersion("v1.0.0"),
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullGraphVersion() {
        assertThrows(IllegalArgumentException.class, () ->
                selectionStrategy.select(
                        List.of(candidate("node-001", CandidateClassification.NEXT_LEARNING)),
                        new StudentId("student-001"),
                        null,
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullCorrelationId() {
        assertThrows(IllegalArgumentException.class, () ->
                selectionStrategy.select(
                        List.of(candidate("node-001", CandidateClassification.NEXT_LEARNING)),
                        new StudentId("student-001"),
                        new GraphVersion("v1.0.0"),
                        null
                )
        );
    }

    private LearningCandidate candidate(
            String nodeId,
            CandidateClassification classification
    ) {
        return new LearningCandidate(
                new NodeId(nodeId),
                classification
        );
    }
}