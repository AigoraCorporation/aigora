package com.aigora.tutororchestrator.domain.valueobjects;

/**
 * External identifier of the Learning Session that originated an orchestration request.
 *
 * <p>This value object is a reference used by the Tutor Orchestrator. Its
 * existence does not transfer ownership of the referenced concept to this
 * bounded context.</p>
 */
public record LearningSessionId(String value) {

    public LearningSessionId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                    "LearningSessionId must not be null or blank"
            );
        }

        value = value.trim();
    }

    @Override
    public String toString() {
        return value;
    }
}
