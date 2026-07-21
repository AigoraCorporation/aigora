package com.aigora.tutororchestrator.shared.validation;

import java.util.Collection;

/**
 * Small framework-independent precondition utility.
 *
 * <p>Use this class for structural invariants such as required constructor
 * dependencies. Domain-specific validation should remain close to the domain
 * object that owns the invariant.</p>
 */
public final class Require {

    private Require() {
    }

    public static <T> T nonNull(
            T value,
            String fieldName
    ) {
        if (value == null) {
            throw new IllegalArgumentException(
                    fieldName + " must not be null"
            );
        }

        return value;
    }

    public static String nonBlank(
            String value,
            String fieldName
    ) {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException(
                    fieldName + " must not be null or blank"
            );
        }

        return value.trim();
    }

    public static <T, C extends Collection<T>> C nonNullCollection(
            C values,
            String fieldName
    ) {
        return nonNull(values, fieldName);
    }

    public static <T, C extends Collection<T>> C withoutNullElements(
            C values,
            String fieldName
    ) {
        nonNull(values, fieldName);

        if (values.stream().anyMatch(element -> element == null)) {
            throw new IllegalArgumentException(
                    fieldName + " must not contain null elements"
            );
        }

        return values;
    }

    public static void condition(
            boolean condition,
            String message
    ) {
        if (!condition) {
            throw new IllegalArgumentException(message);
        }
    }
}