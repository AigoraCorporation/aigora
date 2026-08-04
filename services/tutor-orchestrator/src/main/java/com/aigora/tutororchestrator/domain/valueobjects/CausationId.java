package com.aigora.tutororchestrator.domain.valueobjects;

/**
 * Identifier of the command or event that directly caused the orchestration request.
 *
 * <p>This value object is a reference used by the Tutor Orchestrator. Its
 * existence does not transfer ownership of the referenced concept to this
 * bounded context.</p>
 */
public record CausationId(String value) {

    public CausationId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                    "CausationId must not be null or blank"
            );
        }

        value = value.trim();
    }

    @Override
    public String toString() {
        return value;
    }
}
