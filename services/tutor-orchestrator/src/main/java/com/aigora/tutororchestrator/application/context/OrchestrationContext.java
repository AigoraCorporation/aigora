package com.aigora.tutororchestrator.application.context;

import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

/**
 * Shared application context associated with a deterministic orchestration
 * execution.
 *
 * <p>This context groups identifiers that are propagated across application
 * commands and orchestration flows. It remains independent from transport,
 * infrastructure, persistence, and framework-specific concepts.</p>
 */
public record OrchestrationContext(
        StudentId studentId,
        GraphVersion graphVersion,
        CorrelationId correlationId
) {

    public OrchestrationContext {
        if (studentId == null) {
            throw new IllegalArgumentException(
                    "StudentId must not be null"
            );
        }

        if (graphVersion == null) {
            throw new IllegalArgumentException(
                    "GraphVersion must not be null"
            );
        }

        if (correlationId == null) {
            throw new IllegalArgumentException(
                    "CorrelationId must not be null"
            );
        }
    }
}