package com.aigora.tutororchestrator.testsupport.fixture;

import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;

public final class Candidates {

    public static final LearningCandidate NEXT_CANDIDATE =
            new LearningCandidate(Nodes.NEXT_NODE, CandidateClassification.NEXT_LEARNING);

    public static final LearningCandidate REVIEW_CANDIDATE =
            new LearningCandidate(Nodes.REVIEW_NODE, CandidateClassification.REVIEW);

    public static final LearningCandidate REGRESSION_CANDIDATE =
            new LearningCandidate(Nodes.REGRESSION_NODE, CandidateClassification.REGRESSION);

    private Candidates() {
    }
}