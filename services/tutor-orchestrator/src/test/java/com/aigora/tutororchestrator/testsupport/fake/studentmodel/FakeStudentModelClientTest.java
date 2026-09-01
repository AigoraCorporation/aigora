package com.aigora.tutororchestrator.testsupport.fake.studentmodel;

import com.aigora.tutororchestrator.application.ports.StudentModelClient;
import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class FakeStudentModelClientTest {

    @Test
    void shouldExposeVersionedStudentModelSnapshotUsingDomainSafeTypes() {
        StudentModelClient client = new FakeStudentModelClient();
        var studentId = new StudentId("student-001");

        StudentLearningState state = client.getLearningState(studentId);

        assertEquals(studentId, state.studentId());
        assertEquals(new NodeId("node-001"), state.currentNodeId());
        assertEquals(new GraphVersion("v1.0.0"), state.graphVersion());
        assertEquals(new StudentModelVersion("student-model-v1"), state.studentModelVersion());
        assertTrue(state.currentNodeCompleted());
        assertFalse(state.regressionRecommended());
    }

    @Test
    void shouldExposeRegressionRecommendationFromSameSnapshot() {
        StudentModelClient client = new FakeStudentModelClient(true);

        StudentLearningState state = client.getLearningState(
                new StudentId("student-001")
        );

        assertTrue(state.regressionRecommended());
    }
}
