package com.aigora.tutororchestrator.domain.model;

public record DecisionReason(String code, String description) {
    public DecisionReason {
        if (code == null || code.isBlank()) {
            throw new IllegalArgumentException("DecisionReason code must not be null or blank");
        }
        if (description == null || description.isBlank()) {
            throw new IllegalArgumentException("DecisionReason description must not be null or blank");
        }

        code = code.trim();
        description = description.trim();
    }
}