package com.aigora.tutororchestrator.domain.valueobjects;
import com.aigora.tutororchestrator.shared.validation.Require;
public record CommandId(String value) {
    public CommandId { value = Require.nonBlank(value, "CommandId"); }
    @Override public String toString() { return value; }
}
