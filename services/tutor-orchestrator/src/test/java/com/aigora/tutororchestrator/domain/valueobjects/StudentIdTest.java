package com.aigora.tutororchestrator.domain.valueobjects;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class StudentIdTest {

    @Test
    void shouldCreateStudentId() {
        StudentId studentId = new StudentId("student-001");

        assertEquals("student-001", studentId.value());
    }

    @Test
    void shouldCompareByValue() {
        StudentId first = new StudentId("student-001");
        StudentId second = new StudentId("student-001");

        assertEquals(first, second);
    }

    @Test
    void shouldRejectBlankValue() {
        assertThrows(IllegalArgumentException.class, () -> new StudentId(""));
    }

    @Test
    void shouldRejectNullValue() {
        assertThrows(IllegalArgumentException.class, () -> new StudentId(null));
    }
}