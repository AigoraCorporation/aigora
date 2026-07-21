package com.aigora.tutororchestrator.application.error;

public record AssessmentUnavailable(String message)
        implements ApplicationError {

    private static final String DEFAULT_MESSAGE =
            "Assessment service is currently unavailable";

    public AssessmentUnavailable {
        message = normalize(message, DEFAULT_MESSAGE);
    }

    public AssessmentUnavailable() {
        this(DEFAULT_MESSAGE);
    }

    @Override
    public ApplicationErrorCode code() {
        return ApplicationErrorCode.ASSESSMENT_UNAVAILABLE;
    }

    private static String normalize(String message, String defaultMessage) {
        if (message == null || message.isBlank()) {
            return defaultMessage;
        }

        return message.trim();
    }
}