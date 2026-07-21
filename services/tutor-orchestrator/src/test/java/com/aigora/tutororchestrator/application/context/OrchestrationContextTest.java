package com.aigora.tutororchestrator.application.context;

import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class OrchestrationContextTest {

    @Test
    void shouldCreateContext() {
        var context = new OrchestrationContext(
                new StudentId("student-001"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("correlation-001")
        );

        assertEquals(
                new StudentId("student-001"),
                context.studentId()
        );
        assertEquals(
                new GraphVersion("v1.0.0"),
                context.graphVersion()
        );
        assertEquals(
                new CorrelationId("correlation-001"),
                context.correlationId()
        );
    }

    @Test
    void shouldCompareByValue() {
        var first = context();
        var second = context();

        assertEquals(first, second);
    }

    @Test
    void shouldRejectNullStudentId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationContext(
                        null,
                        new GraphVersion("v1.0.0"),
                        new CorrelationId("correlation-001")
                )
        );
    }

    @Test
    void shouldRejectNullGraphVersion() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationContext(
                        new StudentId("student-001"),
                        null,
                        new CorrelationId("correlation-001")
                )
        );
    }

    @Test
    void shouldRejectNullCorrelationId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationContext(
                        new StudentId("student-001"),
                        new GraphVersion("v1.0.0"),
                        null
                )
        );
    }

    private OrchestrationContext context() {
        return new OrchestrationContext(
                new StudentId("student-001"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("correlation-001")
        );
    }
}