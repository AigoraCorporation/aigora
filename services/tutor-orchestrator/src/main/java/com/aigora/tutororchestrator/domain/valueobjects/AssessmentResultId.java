package com.aigora.tutororchestrator.domain.valueobjects;

/**
 * External identifier of the assessment result used by the orchestration decision.
 *
 * <p>This value object is a reference used by the Tutor Orchestrator. Its
 * existence does not transfer ownership of the referenced concept to this
 * bounded context.</p>
 */
public record AssessmentResultId(String value) {

    public AssessmentResultId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                    "AssessmentResultId must not be null or blank"
            );
        }

        value = value.trim();
    }

    @Override
    public String toString() {
        return value;
    }
}
