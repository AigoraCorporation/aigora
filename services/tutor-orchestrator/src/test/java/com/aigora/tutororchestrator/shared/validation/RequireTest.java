package com.aigora.tutororchestrator.shared.validation;

import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class RequireTest {

    @Test
    void shouldReturnNonNullValue() {
        assertEquals(
                "value",
                Require.nonNull("value", "Field")
        );
    }

    @Test
    void shouldRejectNullValue() {
        var error = assertThrows(
                IllegalArgumentException.class,
                () -> Require.nonNull(null, "Field")
        );

        assertEquals(
                "Field must not be null",
                error.getMessage()
        );
    }

    @Test
    void shouldReturnTrimmedNonBlankValue() {
        assertEquals(
                "value",
                Require.nonBlank("  value  ", "Field")
        );
    }

    @Test
    void shouldRejectBlankValue() {
        assertThrows(
                IllegalArgumentException.class,
                () -> Require.nonBlank(" ", "Field")
        );
    }

    @Test
    void shouldAcceptCollectionWithoutNullElements() {
        var values = List.of("first", "second");

        assertSame(
                values,
                Require.withoutNullElements(values, "Values")
        );
    }

    @Test
    void shouldRejectCollectionContainingNull() {
        var values = new java.util.ArrayList<String>();
        values.add("first");
        values.add(null);

        assertThrows(
                IllegalArgumentException.class,
                () -> Require.withoutNullElements(values, "Values")
        );
    }

    @Test
    void shouldAcceptValidCondition() {
        assertDoesNotThrow(
                () -> Require.condition(true, "Invalid condition")
        );
    }

    @Test
    void shouldRejectInvalidCondition() {
        var error = assertThrows(
                IllegalArgumentException.class,
                () -> Require.condition(false, "Invalid condition")
        );

        assertEquals("Invalid condition", error.getMessage());
    }
}