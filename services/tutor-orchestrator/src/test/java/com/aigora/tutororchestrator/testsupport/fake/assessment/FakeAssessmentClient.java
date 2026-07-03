package com.aigora.tutororchestrator.testsupport.fake.assessment;

import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

public final class FakeAssessmentClient implements AssessmentClient {

    private final boolean masteredCurrentNode;
    private final boolean failedCurrentNode;

    public FakeAssessmentClient(boolean masteredCurrentNode, boolean failedCurrentNode) {
        this.masteredCurrentNode = masteredCurrentNode;
        this.failedCurrentNode = failedCurrentNode;
    }

    @Override
    public boolean hasMasteredNode(StudentId studentId, NodeId nodeId) {
        return masteredCurrentNode;
    }

    @Override
    public boolean hasFailedNode(StudentId studentId, NodeId nodeId) {
        return failedCurrentNode;
    }
}