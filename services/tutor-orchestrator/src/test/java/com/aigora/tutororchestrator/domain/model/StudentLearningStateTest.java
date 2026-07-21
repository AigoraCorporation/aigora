package com.aigora.tutororchestrator.domain.model;

import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class StudentLearningStateTest {

    @Test
    void shouldCreateStudentLearningState() {
        StudentLearningState state = new StudentLearningState(
                new StudentId("student-001"),
                new NodeId("node-001"),
                new GraphVersion("v1.0.0")
        );

        assertEquals(new StudentId("student-001"), state.studentId());
        assertEquals(new NodeId("node-001"), state.currentNodeId());
        assertEquals(new GraphVersion("v1.0.0"), state.graphVersion());
    }

    @Test
    void shouldCompareByValue() {
        StudentLearningState first = new StudentLearningState(
                new StudentId("student-001"),
                new NodeId("node-001"),
                new GraphVersion("v1.0.0")
        );

        StudentLearningState second = new StudentLearningState(
                new StudentId("student-001"),
                new NodeId("node-001"),
                new GraphVersion("v1.0.0")
        );

        assertEquals(first, second);
    }

    @Test
    void shouldRejectNullStudentId() {
        assertThrows(IllegalArgumentException.class, () ->
                new StudentLearningState(
                        null,
                        new NodeId("node-001"),
                        new GraphVersion("v1.0.0")
                )
        );
    }

    @Test
    void shouldRejectNullCurrentNodeId() {
        assertThrows(IllegalArgumentException.class, () ->
                new StudentLearningState(
                        new StudentId("student-001"),
                        null,
                        new GraphVersion("v1.0.0")
                )
        );
    }

    @Test
    void shouldRejectNullGraphVersion() {
        assertThrows(IllegalArgumentException.class, () ->
                new StudentLearningState(
                        new StudentId("student-001"),
                        new NodeId("node-001"),
                        null
                )
        );
    }
}