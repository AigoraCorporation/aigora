package com.aigora.tutororchestrator.domain.valueobjects;

import java.util.UUID;

public record CorrelationId(String value) {

    public CorrelationId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("CorrelationId must not be null or blank");
        }

        value = value.trim();
    }

    public static CorrelationId generate() {
        return new CorrelationId(UUID.randomUUID().toString());
    }

    @Override
    public String toString() {
        return value;
    }
}