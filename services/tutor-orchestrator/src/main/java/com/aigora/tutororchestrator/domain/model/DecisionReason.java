package com.aigora.tutororchestrator.domain.model;

/**
 * Immutable explanation associated with an orchestration decision.
 */
public record DecisionReason(
        String code,
        String description
) {

    public DecisionReason {
        if (code == null || code.isBlank()) {
            throw new IllegalArgumentException(
                    "DecisionReason code must not be null or blank"
            );
        }

        if (description == null || description.isBlank()) {
            throw new IllegalArgumentException(
                    "DecisionReason description must not be null or blank"
            );
        }

        code = code.trim();
        description = description.trim();
    }

    /**
     * Creates a decision reason from a stable reason code.
     *
     * <p>This constructor is intentionally preserved to keep existing
     * application and test code source-compatible.</p>
     */
    public DecisionReason(
            DecisionReasonCode code,
            String description
    ) {
        this(requireCode(code), description);
    }

    private static String requireCode(DecisionReasonCode code) {
        if (code == null) {
            throw new IllegalArgumentException(
                    "DecisionReasonCode must not be null"
            );
        }

        return code.value();
    }
}