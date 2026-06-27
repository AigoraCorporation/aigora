package com.aigora.tutororchestrator.application.contracts.result;

import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;

public record SelectRegressionNodeResult(
        OrchestrationDecision decision
) {
    public SelectRegressionNodeResult {
        if (decision == null) throw new IllegalArgumentException("Decision must not be null");
    }
}