package com.aigora.tutororchestrator.domain.valueobjects;
import com.aigora.tutororchestrator.shared.validation.Require;
public record EventId(String value) {
    public EventId { value = Require.nonBlank(value, "EventId"); }
    @Override public String toString() { return value; }
}
