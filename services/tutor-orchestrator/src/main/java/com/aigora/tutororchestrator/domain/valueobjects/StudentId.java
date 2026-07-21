package com.aigora.tutororchestrator.domain.valueobjects;

public record StudentId(String value) {

    public StudentId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("StudentId must not be null or blank");
        }

        value = value.trim();
    }

    @Override
    public String toString() {
        return value;
    }
}