package com.aigora.tutororchestrator.testsupport.fake.assessment;

import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

public class FakeAssessmentClientTest {

    @Test
    public void shouldExposeAssessmentOperationsUsingDomainSafeTypes() {
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