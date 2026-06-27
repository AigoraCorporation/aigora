package com.aigora.tutororchestrator.domain.policy;

import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.model.StudentLearningState;

public final class EligibilityPolicy {

    public boolean isEligible(
            StudentLearningState studentLearningState,
            LearningCandidate candidate
    ) {
        if (studentLearningState == null) {
            throw new IllegalArgumentException("StudentLearningState must not be null");
        }

        if (candidate == null) {
            throw new IllegalArgumentException("LearningCandidate must not be null");
        }

        return !studentLearningState.currentNodeId().equals(candidate.nodeId());
    }
}