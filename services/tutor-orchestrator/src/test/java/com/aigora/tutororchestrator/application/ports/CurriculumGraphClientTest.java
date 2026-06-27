package com.aigora.tutororchestrator.application.ports;

import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class CurriculumGraphClientTest {

    @Test
    void shouldExposeCurriculumGraphOperationsUsingDomainSafeTypes() {
        CurriculumGraphClient client = new FakeCurriculumGraphClient();

        var studentId = new StudentId("student-001");
        var currentNodeId = new NodeId("node-001");
        var graphVersion = new GraphVersion("v1.0.0");

        assertEquals(currentNodeId, client.getCurrentLearningNode(studentId, graphVersion));

        assertEquals(
                List.of(new NodeId("node-prerequisite-001")),
                client.getPrerequisites(currentNodeId, graphVersion)
        );

        assertEquals(
                List.of(new LearningCandidate(new NodeId("node-002"), CandidateClassification.NEXT_LEARNING)),
                client.getNextCandidateLearningNodes(currentNodeId, studentId, graphVersion)
        );

        assertEquals(
                List.of(new NodeId("node-002")),
                client.getUnlockedNodes(studentId, graphVersion)
        );

        assertTrue(client.nodeExists(currentNodeId, graphVersion));
    }

    private static final class FakeCurriculumGraphClient implements CurriculumGraphClient {

        @Override
        public NodeId getCurrentLearningNode(StudentId studentId, GraphVersion graphVersion) {
            return new NodeId("node-001");
        }

        @Override
        public List<NodeId> getPrerequisites(NodeId nodeId, GraphVersion graphVersion) {
            return List.of(new NodeId("node-prerequisite-001"));
        }

        @Override
        public List<LearningCandidate> getNextCandidateLearningNodes(
                NodeId currentNodeId,
                StudentId studentId,
                GraphVersion graphVersion
        ) {
            return List.of(new LearningCandidate(new NodeId("node-002"), CandidateClassification.NEXT_LEARNING));
        }

        @Override
        public List<NodeId> getUnlockedNodes(StudentId studentId, GraphVersion graphVersion) {
            return List.of(new NodeId("node-002"));
        }

        @Override
        public boolean nodeExists(NodeId nodeId, GraphVersion graphVersion) {
            return true;
        }
    }
}