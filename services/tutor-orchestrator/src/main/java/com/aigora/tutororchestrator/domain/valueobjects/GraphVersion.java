package com.aigora.tutororchestrator.domain.valueobjects;

public record GraphVersion(String value) {

    public GraphVersion {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("GraphVersion must not be null or blank");
        }

        value = value.trim();
    }

    @Override
    public String toString() {
        return value;
    }
}