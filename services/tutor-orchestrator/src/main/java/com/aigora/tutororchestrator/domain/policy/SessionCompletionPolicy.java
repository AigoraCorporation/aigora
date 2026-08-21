package com.aigora.tutororchestrator.domain.policy;

import com.aigora.tutororchestrator.domain.model.OrchestrationOutcome;

public final class SessionCompletionPolicy {
    public boolean shouldComplete(OrchestrationOutcome outcome) {
        return outcome == OrchestrationOutcome.COMPLETED;
    }
}
