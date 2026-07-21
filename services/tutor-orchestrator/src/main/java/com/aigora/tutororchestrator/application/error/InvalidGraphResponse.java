package com.aigora.tutororchestrator.application.error;

public record InvalidGraphResponse(String message) implements ApplicationError {

    private static final String DEFAULT_MESSAGE =
            "Curriculum Graph returned an invalid response";

    public InvalidGraphResponse {
        message = normalize(message, DEFAULT_MESSAGE);
    }

    public InvalidGraphResponse() {
        this(DEFAULT_MESSAGE);
    }

    @Override
    public ApplicationErrorCode code() {
        return ApplicationErrorCode.INVALID_GRAPH_RESPONSE;
    }

    private static String normalize(String message, String defaultMessage) {
        if (message == null || message.isBlank()) {
            return defaultMessage;
        }

        return message.trim();
    }
}