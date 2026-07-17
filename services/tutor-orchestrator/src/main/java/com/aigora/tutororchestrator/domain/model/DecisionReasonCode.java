package com.aigora.tutororchestrator.domain.model;

/**
 * Stable reason codes used to explain deterministic orchestration decisions.
 *
 * <p>The enum owns the canonical serialized value of each reason while
 * keeping the human-readable description outside the code itself.</p>
 */
public enum DecisionReasonCode {

    CANDIDATE_SELECTED,
    NO_CANDIDATE_AVAILABLE,
    LEARNING_COMPLETED,
    LEARNING_IN_PROGRESS,
    REGRESSION_RECOMMENDED;

    public String value() {
        return name();
    }
}