package com.aigora.tutororchestrator.application.error;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

class StudentModelUnavailableTest {

    @Test
    void shouldReturnStudentModelUnavailableCode() {
        var error = new StudentModelUnavailable();

        assertEquals(
                ApplicationErrorCode.STUDENT_MODEL_UNAVAILABLE,
                error.code()
        );
    }

    @Test
    void shouldUseDefaultMessage() {
        var error = new StudentModelUnavailable();

        assertEquals(
                "Student Model is currently unavailable",
                error.message()
        );
    }

    @Test
    void shouldUseCustomMessage() {
        var error = new StudentModelUnavailable(
                "Student Model could not be contacted"
        );

        assertEquals(
                "Student Model could not be contacted",
                error.message()
        );
    }

    @Test
    void shouldTrimCustomMessage() {
        var error = new StudentModelUnavailable(
                "  Student Model could not be contacted  "
        );

        assertEquals(
                "Student Model could not be contacted",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultMessageWhenMessageIsNull() {
        var error = new StudentModelUnavailable(null);

        assertEquals(
                "Student Model is currently unavailable",
                error.message()
        );
    }

    @Test
    void shouldUseDefaultMessageWhenMessageIsBlank() {
        var error = new StudentModelUnavailable("   ");

        assertEquals(
                "Student Model is currently unavailable",
                error.message()
        );
    }

    @Test
    void shouldCompareByValue() {
        var first = new StudentModelUnavailable("Student Model unavailable");
        var second = new StudentModelUnavailable("Student Model unavailable");

        assertEquals(first, second);
    }
}