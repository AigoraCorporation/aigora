package com.aigora.tutororchestrator.testsupport.fake.studentmodel;
import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.application.ports.StudentModelClient;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class FakeStudentModelClientTest {

    @Test
    public void shouldExposeStudentModelOperationsUsingDomainSafeTypes() {
        StudentModelClient client = new FakeStudentModelClient();

        var studentId = new StudentId("student-001");

        assertEquals(
                new StudentLearningState(
                        new StudentId("student-001"),
                        new NodeId("node-001"),
                        new GraphVersion("v1.0.0")
                ),
                client.getLearningState(studentId)
        );

        assertTrue(client.hasCompletedCurrentNode(studentId));
        assertFalse(client.isRegressionRecommended(studentId));
    }

    private static final class FakeStudentModelClient implements StudentModelClient {

        @Override
        public StudentLearningState getLearningState(StudentId studentId) {
            return new StudentLearningState(
                    studentId,
                    new NodeId("node-001"),
                    new GraphVersion("v1.0.0")
            );
        }

        @Override
        public boolean hasCompletedCurrentNode(StudentId studentId) {
            return true;
        }

        @Override
        public boolean isRegressionRecommended(StudentId studentId) {
            return false;
        }
    }
}