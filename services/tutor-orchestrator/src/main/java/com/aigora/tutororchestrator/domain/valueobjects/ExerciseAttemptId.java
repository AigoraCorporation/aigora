package com.aigora.tutororchestrator.domain.valueobjects;

/**
 * External identifier of the exercise attempt used as decision evidence.
 *
 * <p>This value object is a reference used by the Tutor Orchestrator. Its
 * existence does not transfer ownership of the referenced concept to this
 * bounded context.</p>
 */
public record ExerciseAttemptId(String value) {

    public ExerciseAttemptId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                    "ExerciseAttemptId must not be null or blank"
            );
        }

        value = value.trim();
    }

    @Override
    public String toString() {
        return value;
    }
}
