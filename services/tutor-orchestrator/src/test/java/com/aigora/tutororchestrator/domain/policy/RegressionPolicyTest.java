package com.aigora.tutororchestrator.domain.policy;

import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class RegressionPolicyTest {

    private final RegressionPolicy policy = new RegressionPolicy();

    @Test
    void shouldRegressWhenCurrentNodeFailed() {
        assertTrue(policy.shouldRegress(true, false));
    }

    @Test
    void shouldRegressWhenRegressionIsRecommended() {
        assertTrue(policy.shouldRegress(false, true));
    }

    @Test
    void shouldRegressWhenCurrentNodeFailedAndRegressionIsRecommended() {
        assertTrue(policy.shouldRegress(true, true));
    }

    @Test
    void shouldNotRegressWhenCurrentNodeDidNotFailAndRegressionIsNotRecommended() {
        assertFalse(policy.shouldRegress(false, false));
    }

    @Test
    void shouldIdentifyRegressionCandidate() {
        var candidate = new LearningCandidate(
                new NodeId("node-prerequisite-001"),
                CandidateClassification.REGRESSION
        );

        assertTrue(policy.isRegressionCandidate(candidate));
    }

    @Test
    void shouldNotIdentifyNonRegressionCandidate() {
        var candidate = new LearningCandidate(
                new NodeId("node-002"),
                CandidateClassification.NEXT_LEARNING
        );

        assertFalse(policy.isRegressionCandidate(candidate));
    }

    @Test
    void shouldRejectNullCandidate() {
        assertThrows(IllegalArgumentException.class, () ->
                policy.isRegressionCandidate(null)
        );
    }

    @Test
    void shouldBeDeterministicForSameInput() {
        assertEquals(
                policy.shouldRegress(true, false),
                policy.shouldRegress(true, false)
        );

        var candidate = new LearningCandidate(
                new NodeId("node-prerequisite-001"),
                CandidateClassification.REGRESSION
        );

        assertEquals(
                policy.isRegressionCandidate(candidate),
                policy.isRegressionCandidate(candidate)
        );
    }
}