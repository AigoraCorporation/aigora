package com.aigora.tutororchestrator.domain.valueobjects;

public record NodeId(String value) {

    public NodeId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("NodeId must not be null or blank");
        }

        value = value.trim();
    }

    @Override
    public String toString() {
        return value;
    }
}