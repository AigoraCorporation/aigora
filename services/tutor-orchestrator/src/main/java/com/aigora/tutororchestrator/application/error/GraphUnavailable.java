package com.aigora.tutororchestrator.application.error;

public record GraphUnavailable(String message) implements ApplicationError {

    private static final String DEFAULT_MESSAGE =
            "Curriculum Graph is currently unavailable";

    public GraphUnavailable {
        message = normalize(message, DEFAULT_MESSAGE);
    }

    public GraphUnavailable() {
        this(DEFAULT_MESSAGE);
    }

    @Override
    public ApplicationErrorCode code() {
        return ApplicationErrorCode.GRAPH_UNAVAILABLE;
    }

    private static String normalize(String message, String defaultMessage) {
        if (message == null || message.isBlank()) {
            return defaultMessage;
        }

        return message.trim();
    }
}