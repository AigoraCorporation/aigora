package com.aigora.tutororchestrator.domain.valueobjects;

/**
 * Immutable version of the Student Model snapshot used by the decision.
 *
 * <p>This value object is a reference used by the Tutor Orchestrator. Its
 * existence does not transfer ownership of the referenced concept to this
 * bounded context.</p>
 */
public record StudentModelVersion(String value) {

    public StudentModelVersion {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                    "StudentModelVersion must not be null or blank"
            );
        }

        value = value.trim();
    }

    @Override
    public String toString() {
        return value;
    }
}
