package com.aigora.tutororchestrator.application.error;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class DependencyTimeoutTest {

    @Test
    void shouldReturnDependencyTimeoutCode() {
        var error = new DependencyTimeout("Curriculum Graph");

        assertEquals(
                ApplicationErrorCode.DEPENDENCY_TIMEOUT,
                error.code()
        );
    }

    @Test
    void shouldUseProvidedDependencyName() {
        var error = new DependencyTimeout("Curriculum Graph");

        assertEquals(
                "Curriculum Graph",
                error.dependencyName()
        );
    }

    @Test
    void shouldGenerateDefaultMessageFromDependencyName() {
        var error = new DependencyTimeout("Curriculum Graph");

        assertEquals(
                "Curriculum Graph did not respond within the expected time",
                error.message()
        );
    }

    @Test
    void shouldUseCustomMessage() {
        var error = new DependencyTimeout(
                "Student Model",
                "Student Model exceeded the configured timeout"
        );

        assertEquals(
                "Student Model exceeded the configured timeout",
                error.message()
        );
    }

    @Test
    void shouldTrimDependencyNameAndCustomMessage() {
        var error = new DependencyTimeout(
                "  Student Model  ",
                "  Dependency timed out  "
        );

        assertEquals("Student Model", error.dependencyName());
        assertEquals("Dependency timed out", error.message());
    }

    @Test
    void shouldUseDefaultDependencyNameWhenNameIsNull() {
        var error = new DependencyTimeout(null);

        assertEquals(
                "external dependency",
                error.dependencyName()
        );

        assertEquals(
                "external dependency did not respond within the expected time",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultDependencyNameWhenNameIsBlank() {
        var error = new DependencyTimeout("   ");

        assertEquals(
                "external dependency",
                error.dependencyName()
        );

        assertEquals(
                "external dependency did not respond within the expected time",
                error.message()
        );
    }

    @Test
    void shouldGenerateDefaultMessageWhenCustomMessageIsNull() {
        var error = new DependencyTimeout(
                "Assessment",
                null
        );

        assertEquals(
                "Assessment did not respond within the expected time",
                error.message()
        );
    }

    @Test
    void shouldGenerateDefaultMessageWhenCustomMessageIsBlank() {
        var error = new DependencyTimeout(
                "Assessment",
                "   "
        );

        assertEquals(
                "Assessment did not respond within the expected time",
                error.message()
        );
    }

    @Test
    void shouldCompareByValue() {
        var first = new DependencyTimeout(
                "Assessment",
                "Assessment timed out"
        );

        var second = new DependencyTimeout(
                "Assessment",
                "Assessment timed out"
        );

        assertEquals(first, second);
    }
}