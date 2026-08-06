package com.aigora.tutororchestrator.application.context;

import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.OrchestrationRequestId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

/**
 * Shared application context associated with a deterministic orchestration
 * execution.
 *
 * <p>This context groups identifiers, session references, decision evidence,
 * and tracing metadata propagated across application commands and
 * orchestration flows.</p>
 *
 * <p>It remains independent from transport, infrastructure, persistence,
 * and framework-specific concepts.</p>
 */
public record OrchestrationContext(
        OrchestrationRequestId requestId,
        StudentId studentId,
        LearningSessionReference sessionReference,
        DecisionEvidenceContext decisionEvidence,
        TraceContext traceContext
) {

    public OrchestrationContext {
        if (requestId == null) {
            throw new IllegalArgumentException(
                    "OrchestrationRequestId must not be null"
            );
        }

        if (studentId == null) {
            throw new IllegalArgumentException(
                    "StudentId must not be null"
            );
        }

        if (sessionReference == null) {
            throw new IllegalArgumentException(
                    "LearningSessionReference must not be null"
            );
        }

        if (decisionEvidence == null) {
            throw new IllegalArgumentException(
                    "DecisionEvidenceContext must not be null"
            );
        }

        if (traceContext == null) {
            throw new IllegalArgumentException(
                    "TraceContext must not be null"
            );
        }
    }

    /**
     * Temporary compatibility accessor.
     *
     * <p>Allows existing code to continue using {@code context.graphVersion()}
     * while the orchestration pipeline is migrated to the nested evidence
     * context.</p>
     */
    public GraphVersion graphVersion() {
        return decisionEvidence.graphVersion();
    }

    /**
     * Temporary compatibility accessor.
     *
     * <p>Allows existing code to continue using
     * {@code context.correlationId()} while the orchestration pipeline is
     * migrated to the nested trace context.</p>
     */
    public CorrelationId correlationId() {
        return traceContext.correlationId();
    }
}