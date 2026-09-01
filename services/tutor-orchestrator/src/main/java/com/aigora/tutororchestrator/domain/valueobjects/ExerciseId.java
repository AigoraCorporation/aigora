package com.aigora.tutororchestrator.domain.valueobjects;
import com.aigora.tutororchestrator.shared.validation.Require;
public record ExerciseId(String value) {
    public ExerciseId { value = Require.nonBlank(value, "ExerciseId"); }
    @Override public String toString() { return value; }
}
