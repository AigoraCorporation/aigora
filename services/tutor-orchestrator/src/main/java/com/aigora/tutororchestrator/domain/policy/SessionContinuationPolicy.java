package com.aigora.tutororchestrator.domain.policy;

import com.aigora.tutororchestrator.domain.model.OrchestrationOutcome;

public final class SessionContinuationPolicy {
    public boolean shouldContinue(OrchestrationOutcome outcome) {
        return outcome == OrchestrationOutcome.NEXT_NODE
                || outcome == OrchestrationOutcome.CONTINUE_CURRENT_NODE;
    }
}
