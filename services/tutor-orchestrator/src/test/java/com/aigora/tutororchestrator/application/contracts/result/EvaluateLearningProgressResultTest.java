package com.aigora.tutororchestrator.application.contracts.result;

import com.aigora.tutororchestrator.domain.model.DecisionReason;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class EvaluateLearningProgressResultTest {

    @Test
    void shouldCreateResult() {
        var result = new EvaluateLearningProgressResult(
                new StudentId("student-001"),
                true,
                false,
                new DecisionReason("COMPLETED", "Learning progress completed")
        );

        assertEquals(new StudentId("student-001"), result.studentId());
        assertTrue(result.completed());
        assertFalse(result.regressionRecommended());
        assertEquals(new DecisionReason("COMPLETED", "Learning progress completed"), result.reason());
    }

    @Test
    void shouldCompareByValue() {
        var first = new EvaluateLearningProgressResult(
                new StudentId("student-001"),
                true,
                false,
                new DecisionReason("COMPLETED", "Learning progress completed")
        );

        var second = new EvaluateLearningProgressResult(
                new StudentId("student-001"),
                true,
                false,
                new DecisionReason("COMPLETED", "Learning progress completed")
        );

        assertEquals(first, second);
    }

    @Test
    void shouldRejectNullStudentId() {
        assertThrows(IllegalArgumentException.class, () ->
                new EvaluateLearningProgressResult(
                        null,
                        true,
                        false,
                        new DecisionReason("COMPLETED", "Learning progress completed")
                )
        );
    }

    @Test
    void shouldRejectNullReason() {
        assertThrows(IllegalArgumentException.class, () ->
                new EvaluateLearningProgressResult(
                        new StudentId("student-001"),
                        true,
                        false,
                        null
                )
        );
    }
}