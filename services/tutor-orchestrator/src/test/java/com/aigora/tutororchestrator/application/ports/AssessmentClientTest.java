package com.aigora.tutororchestrator.application.ports;

import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class AssessmentClientTest {

    @Test
    void shouldExposeAssessmentOperationsUsingDomainSafeTypes() {
        AssessmentClient client = new FakeAssessmentClient();

        var studentId = new StudentId("student-001");
        var nodeId = new NodeId("node-001");

        assertTrue(client.hasMasteredNode(studentId, nodeId));
        assertFalse(client.hasFailedNode(studentId, nodeId));
    }

    private static final class FakeAssessmentClient implements AssessmentClient {

        @Override
        public boolean hasMasteredNode(StudentId studentId, NodeId nodeId) {
            return true;
        }

        @Override
        public boolean hasFailedNode(StudentId studentId, NodeId nodeId) {
            return false;
        }
    }
}