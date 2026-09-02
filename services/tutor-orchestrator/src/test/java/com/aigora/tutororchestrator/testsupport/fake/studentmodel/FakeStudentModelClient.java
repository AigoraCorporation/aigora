package com.aigora.tutororchestrator.testsupport.fake.studentmodel;

import com.aigora.tutororchestrator.application.ports.StudentModelClient;
import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;

public final class FakeStudentModelClient implements StudentModelClient {

    private final boolean regressionRecommended;

    public FakeStudentModelClient() {
        this(false);
    }

    public FakeStudentModelClient(boolean regressionRecommended) {
        this.regressionRecommended = regressionRecommended;
    }

    @Override
    public StudentLearningState getLearningState(StudentId studentId) {
        return new StudentLearningState(
                studentId,
                new NodeId("node-001"),
                new GraphVersion("v1.0.0"),
                new StudentModelVersion("student-model-v1"),
                true,
                regressionRecommended
        );
    }
}
