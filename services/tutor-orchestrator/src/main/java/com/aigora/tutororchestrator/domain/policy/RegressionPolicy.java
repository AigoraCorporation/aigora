package com.aigora.tutororchestrator.domain.policy;

import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;

public final class RegressionPolicy {

    public boolean shouldRegress(
            boolean failedCurrentNode,
            boolean regressionRecommended
    ) {
        return failedCurrentNode || regressionRecommended;
    }

    public boolean isRegressionCandidate(LearningCandidate candidate) {
        if (candidate == null) {
            throw new IllegalArgumentException("LearningCandidate must not be null");
        }

        return candidate.classification() == CandidateClassification.REGRESSION;
    }
}