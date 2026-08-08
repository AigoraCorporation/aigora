package com.aigora.tutororchestrator.testsupport.fake.assessment;

import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import com.aigora.tutororchestrator.domain.model.AssessmentSnapshot;
import com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId;
import com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;

import java.math.BigDecimal;

public final class FakeAssessmentClient implements AssessmentClient {

    private AssessmentSnapshot snapshot;

    public FakeAssessmentClient() {
        this(true, false);
    }

    public FakeAssessmentClient(
            boolean masteredCurrentNode,
            boolean failedCurrentNode
    ) {
        this.snapshot = new AssessmentSnapshot(
                new AssessmentResultId("assessment-001"),
                new ExerciseAttemptId("attempt-001"),
                new NodeId("node-001"),
                masteredCurrentNode,
                failedCurrentNode,
                masteredCurrentNode ? BigDecimal.ONE : BigDecimal.ZERO,
                BigDecimal.ONE
        );
    }

    public FakeAssessmentClient(AssessmentSnapshot snapshot) {
        setSnapshot(snapshot);
    }

    public void setSnapshot(AssessmentSnapshot snapshot) {
        if (snapshot == null) {
            throw new IllegalArgumentException(
                    "AssessmentSnapshot must not be null"
            );
        }
        this.snapshot = snapshot;
    }

    @Override
    public AssessmentSnapshot getAssessment(
            AssessmentResultId assessmentResultId
    ) {
        if (assessmentResultId == null) {
            throw new IllegalArgumentException(
                    "AssessmentResultId must not be null"
            );
        }

        if (!snapshot.assessmentResultId().equals(assessmentResultId)) {
            throw new IllegalStateException(
                    "Assessment not found: " + assessmentResultId
            );
        }

        return snapshot;
    }
}
