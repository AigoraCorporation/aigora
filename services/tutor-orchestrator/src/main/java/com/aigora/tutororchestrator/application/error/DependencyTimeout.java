package com.aigora.tutororchestrator.application.error;

public record DependencyTimeout(
        String dependencyName,
        String message
) implements ApplicationError {

    private static final String DEFAULT_DEPENDENCY_NAME =
            "external dependency";

    public DependencyTimeout {
        dependencyName = normalizeDependencyName(dependencyName);
        message = normalizeMessage(message, dependencyName);
    }

    public DependencyTimeout(String dependencyName) {
        this(
                dependencyName,
                "%s did not respond within the expected time"
                        .formatted(normalizeDependencyName(dependencyName))
        );
    }

    @Override
    public ApplicationErrorCode code() {
        return ApplicationErrorCode.DEPENDENCY_TIMEOUT;
    }

    private static String normalizeDependencyName(String dependencyName) {
        if (dependencyName == null || dependencyName.isBlank()) {
            return DEFAULT_DEPENDENCY_NAME;
        }

        return dependencyName.trim();
    }

    private static String normalizeMessage(
            String message,
            String dependencyName
    ) {
        if (message == null || message.isBlank()) {
            return "%s did not respond within the expected time"
                    .formatted(dependencyName);
        }

        return message.trim();
    }
}