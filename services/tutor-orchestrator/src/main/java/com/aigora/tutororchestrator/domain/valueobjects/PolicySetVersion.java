package com.aigora.tutororchestrator.domain.valueobjects;

/**
 * Immutable version of the policy set executed by the Tutor Orchestrator.
 *
 * <p>This value object is a reference used by the Tutor Orchestrator. Its
 * existence does not transfer ownership of the referenced concept to this
 * bounded context.</p>
 */
public record PolicySetVersion(String value) {

    public PolicySetVersion {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                    "PolicySetVersion must not be null or blank"
            );
        }

        value = value.trim();
    }

    @Override
    public String toString() {
        return value;
    }
}
