package com.aigora.tutororchestrator.application.error;

public record NoCandidateAvailable(String message) implements ApplicationError {

    private static final String DEFAULT_MESSAGE =
            "No valid learning candidate is available";

    public NoCandidateAvailable {
        message = normalize(message, DEFAULT_MESSAGE);
    }

    public NoCandidateAvailable() {
        this(DEFAULT_MESSAGE);
    }

    @Override
    public ApplicationErrorCode code() {
        return ApplicationErrorCode.NO_CANDIDATE_AVAILABLE;
    }

    private static String normalize(String message, String defaultMessage) {
        if (message == null || message.isBlank()) {
            return defaultMessage;
        }

        return message.trim();
    }
}