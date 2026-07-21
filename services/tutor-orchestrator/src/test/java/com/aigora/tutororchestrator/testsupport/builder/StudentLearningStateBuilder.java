package com.aigora.tutororchestrator.testsupport.builder;

import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

public final class StudentLearningStateBuilder {

    private StudentId studentId = new StudentId("student-001");
    private NodeId currentNodeId = new NodeId("node-001");
    private GraphVersion graphVersion = new GraphVersion("v1.0.0");

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

    public StudentLearningState build() {
        return new StudentLearningState(studentId, currentNodeId, graphVersion);
    }
}