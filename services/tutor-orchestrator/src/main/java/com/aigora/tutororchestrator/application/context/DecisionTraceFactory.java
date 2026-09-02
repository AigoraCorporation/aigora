package com.aigora.tutororchestrator.application.context;

import com.aigora.tutororchestrator.domain.model.DecisionTrace;

import java.time.Clock;
import java.time.Instant;

public final class DecisionTraceFactory {

    private final Clock clock;

    public DecisionTraceFactory(Clock clock) {
        if (clock == null) {
            throw new IllegalArgumentException(
                    "Clock must not be null"
            );
        }

        this.clock = clock;
    }

    public DecisionTrace create(OrchestrationContext context) {
        if (context == null) {
            throw new IllegalArgumentException(
                    "OrchestrationContext must not be null"
            );
        }

        return new DecisionTrace(
                context.requestId(),
                context.sessionReference().learningSessionId(),
                context.sessionReference().exerciseAttemptId(),
                context.decisionEvidence().assessmentResultId(),
                context.decisionEvidence().studentModelVersion(),
                context.decisionEvidence().graphVersion(),
                context.decisionEvidence().policySetVersion(),
                context.traceContext().correlationId(),
                context.traceContext().causationId(),
                Instant.now(clock)
        );
    }
}