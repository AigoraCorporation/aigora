package com.aigora.tutororchestrator.testsupport.builder;

import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;

public final class StudentLearningStateBuilder {

    private StudentId studentId = new StudentId("student-001");
    private NodeId currentNodeId = new NodeId("node-001");
    private GraphVersion graphVersion = new GraphVersion("v1.0.0");
    private StudentModelVersion studentModelVersion = new StudentModelVersion("student-model-v1");
    private boolean currentNodeCompleted = true;
    private boolean regressionRecommended = false;

    private StudentLearningStateBuilder() {
    }

    public static StudentLearningStateBuilder aStudentLearningState() {
        return new StudentLearningStateBuilder();
    }

    public StudentLearningStateBuilder withStudentId(String studentId) {
        this.studentId = new StudentId(studentId);
        return this;
    }

    public StudentLearningStateBuilder withCurrentNodeId(String currentNodeId) {
        this.currentNodeId = new NodeId(currentNodeId);
        return this;
    }

    public StudentLearningStateBuilder withGraphVersion(String graphVersion) {
        this.graphVersion = new GraphVersion(graphVersion);
        return this;
    }

    public StudentLearningStateBuilder withStudentModelVersion(String studentModelVersion) {
        this.studentModelVersion = new StudentModelVersion(studentModelVersion);
        return this;
    }

    public StudentLearningStateBuilder withCurrentNodeCompleted(boolean currentNodeCompleted) {
        this.currentNodeCompleted = currentNodeCompleted;
        return this;
    }

    public StudentLearningStateBuilder withRegressionRecommended(boolean regressionRecommended) {
        this.regressionRecommended = regressionRecommended;
        return this;
    }

    public StudentLearningState build() {
        return new StudentLearningState(
                studentId,
                currentNodeId,
                graphVersion,
                studentModelVersion,
                currentNodeCompleted,
                regressionRecommended
        );
    }
}