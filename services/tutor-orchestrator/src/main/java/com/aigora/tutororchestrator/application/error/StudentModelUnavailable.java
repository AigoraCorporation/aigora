package com.aigora.tutororchestrator.application.error;

public record StudentModelUnavailable(String message)
        implements ApplicationError {

    private static final String DEFAULT_MESSAGE =
            "Student Model is currently unavailable";

    public StudentModelUnavailable {
        message = normalize(message, DEFAULT_MESSAGE);
    }

    public StudentModelUnavailable() {
        this(DEFAULT_MESSAGE);
    }

    @Override
    public ApplicationErrorCode code() {
        return ApplicationErrorCode.STUDENT_MODEL_UNAVAILABLE;
    }

    private static String normalize(String message, String defaultMessage) {
        if (message == null || message.isBlank()) {
            return defaultMessage;
        }

        return message.trim();
    }
}