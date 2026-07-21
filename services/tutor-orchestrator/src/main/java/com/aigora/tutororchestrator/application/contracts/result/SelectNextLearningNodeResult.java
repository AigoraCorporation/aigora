package com.aigora.tutororchestrator.application.contracts.result;

import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;

public record SelectNextLearningNodeResult(
        OrchestrationDecision decision
) {
    public SelectNextLearningNodeResult {
        if (decision == null) throw new IllegalArgumentException("Decision must not be null");
    }
}