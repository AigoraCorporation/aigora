package com.aigora.tutororchestrator.domain.model;

import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class LearningCandidateTest {

    @Test
    void shouldCreateLearningCandidate() {
        LearningCandidate candidate = new LearningCandidate(
                new NodeId("node-001"),
                CandidateClassification.NEXT_LEARNING
        );

        assertEquals(new NodeId("node-001"), candidate.nodeId());
        assertEquals(CandidateClassification.NEXT_LEARNING, candidate.classification());
    }

    @Test
    void shouldCompareByValue() {
        LearningCandidate first = new LearningCandidate(
                new NodeId("node-001"),
                CandidateClassification.NEXT_LEARNING
        );

        LearningCandidate second = new LearningCandidate(
                new NodeId("node-001"),
                CandidateClassification.NEXT_LEARNING
        );

        assertEquals(first, second);
    }

    @Test
    void shouldRejectNullNodeId() {
        assertThrows(IllegalArgumentException.class, () ->
                new LearningCandidate(null, CandidateClassification.NEXT_LEARNING)
        );
    }

    @Test
    void shouldRejectNullClassification() {
        assertThrows(IllegalArgumentException.class, () ->
                new LearningCandidate(new NodeId("node-001"), null)
        );
    }
}