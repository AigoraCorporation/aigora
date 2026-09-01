package com.aigora.tutororchestrator.domain.policy;

import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class EligibilityPolicyTest {

    private final EligibilityPolicy policy = new EligibilityPolicy();

    @Test
    void shouldReturnEligibleWhenCandidateIsDifferentFromCurrentNode() {
        var state = new StudentLearningState(
                new StudentId("student-001"),
                new NodeId("node-001"),
                new GraphVersion("v1.0.0"),
                new StudentModelVersion("student-model-v1"),
                true,
                false
        );

        var candidate = new LearningCandidate(
                new NodeId("node-002"),
                CandidateClassification.NEXT_LEARNING
        );

        assertTrue(policy.isEligible(state, candidate));
    }

    @Test
    void shouldReturnNotEligibleWhenCandidateIsCurrentNode() {
        var state = new StudentLearningState(
                new StudentId("student-001"),
                new NodeId("node-001"),
                new GraphVersion("v1.0.0"),
                new StudentModelVersion("student-model-v1"),
                true,
                false
        );

        var candidate = new LearningCandidate(
                new NodeId("node-001"),
                CandidateClassification.NEXT_LEARNING
        );

        assertFalse(policy.isEligible(state, candidate));
    }

    @Test
    void shouldRejectNullStudentLearningState() {
        var candidate = new LearningCandidate(
                new NodeId("node-002"),
                CandidateClassification.NEXT_LEARNING
        );

        assertThrows(IllegalArgumentException.class, () ->
                policy.isEligible(null, candidate)
        );
    }

    @Test
    void shouldRejectNullLearningCandidate() {
        var state = new StudentLearningState(
                new StudentId("student-001"),
                new NodeId("node-001"),
                new GraphVersion("v1.0.0"),
                new StudentModelVersion("student-model-v1"),
                true,
                false
        );

        assertThrows(IllegalArgumentException.class, () ->
                policy.isEligible(state, null)
        );
    }

    @Test
    void shouldBeDeterministicForSameInput() {
        var state = new StudentLearningState(
                new StudentId("student-001"),
                new NodeId("node-001"),
                new GraphVersion("v1.0.0"),
                new StudentModelVersion("student-model-v1"),
                true,
                false
        );

        var candidate = new LearningCandidate(
                new NodeId("node-002"),
                CandidateClassification.NEXT_LEARNING
        );

        assertEquals(
                policy.isEligible(state, candidate),
                policy.isEligible(state, candidate)
        );
    }
}