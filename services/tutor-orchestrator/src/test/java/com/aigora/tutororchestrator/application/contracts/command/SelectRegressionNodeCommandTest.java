package com.aigora.tutororchestrator.application.contracts.command;

import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class SelectRegressionNodeCommandTest {

    @Test
    void shouldCreateCommand() {
        var command = new SelectRegressionNodeCommand(
                new StudentId("student-001"),
                new NodeId("node-001"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("corr-001")
        );

        assertEquals(new StudentId("student-001"), command.studentId());
        assertEquals(new NodeId("node-001"), command.currentNodeId());
        assertEquals(new GraphVersion("v1.0.0"), command.graphVersion());
        assertEquals(new CorrelationId("corr-001"), command.correlationId());
    }

    @Test
    void shouldCompareByValue() {
        var first = new SelectRegressionNodeCommand(
                new StudentId("student-001"),
                new NodeId("node-001"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("corr-001")
        );

        var second = new SelectRegressionNodeCommand(
                new StudentId("student-001"),
                new NodeId("node-001"),
                new GraphVersion("v1.0.0"),
                new CorrelationId("corr-001")
        );

        assertEquals(first, second);
    }

    @Test
    void shouldRejectNullStudentId() {
        assertThrows(IllegalArgumentException.class, () ->
                new SelectRegressionNodeCommand(
                        null,
                        new NodeId("node-001"),
                        new GraphVersion("v1.0.0"),
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullCurrentNodeId() {
        assertThrows(IllegalArgumentException.class, () ->
                new SelectRegressionNodeCommand(
                        new StudentId("student-001"),
                        null,
                        new GraphVersion("v1.0.0"),
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullGraphVersion() {
        assertThrows(IllegalArgumentException.class, () ->
                new SelectRegressionNodeCommand(
                        new StudentId("student-001"),
                        new NodeId("node-001"),
                        null,
                        new CorrelationId("corr-001")
                )
        );
    }

    @Test
    void shouldRejectNullCorrelationId() {
        assertThrows(IllegalArgumentException.class, () ->
                new SelectRegressionNodeCommand(
                        new StudentId("student-001"),
                        new NodeId("node-001"),
                        new GraphVersion("v1.0.0"),
                        null
                )
        );
    }
}