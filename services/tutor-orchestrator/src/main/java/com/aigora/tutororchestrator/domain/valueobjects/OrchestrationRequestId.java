package com.aigora.tutororchestrator.domain.valueobjects;

/**
 * Stable identifier of an orchestration request, reused across retries.
 *
 * <p>This value object is a reference used by the Tutor Orchestrator. Its
 * existence does not transfer ownership of the referenced concept to this
 * bounded context.</p>
 */
public record OrchestrationRequestId(String value) {

    public OrchestrationRequestId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                    "OrchestrationRequestId must not be null or blank"
            );
        }

        value = value.trim();
    }

    @Override
    public String toString() {
        return value;
    }
}
