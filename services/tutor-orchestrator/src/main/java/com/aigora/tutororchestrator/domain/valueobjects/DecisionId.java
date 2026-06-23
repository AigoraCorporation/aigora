package com.aigora.tutororchestrator.domain.valueobjects;

import java.util.UUID;

public record DecisionId(String value) {

    public DecisionId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("DecisionId must not be null or blank");
        }

        value = value.trim();
    }

    public static DecisionId generate() {
        return new DecisionId(UUID.randomUUID().toString());
    }

    @Override
    public String toString() {
        return value;
    }
}