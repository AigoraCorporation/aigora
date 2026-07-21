package com.aigora.tutororchestrator.testsupport.fake.curriculumgraph;

import com.aigora.tutororchestrator.application.ports.CurriculumGraphClient;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

import java.util.List;

public final class FakeCurriculumGraphClient implements CurriculumGraphClient {

    private final List<LearningCandidate> candidates;
    private final List<NodeId> prerequisites;

    public FakeCurriculumGraphClient(List<LearningCandidate> candidates) {
        this(candidates, List.of());
    }

    public FakeCurriculumGraphClient(
            List<LearningCandidate> candidates,
            List<NodeId> prerequisites
    ) {
        this.candidates = candidates;
        this.prerequisites = prerequisites;
    }

    @Override
    public NodeId getCurrentLearningNode(StudentId studentId, GraphVersion graphVersion) {
        return new NodeId("node-001");
    }

    @Override
    public List<NodeId> getPrerequisites(NodeId nodeId, GraphVersion graphVersion) {
        return prerequisites;
    }

    @Override
    public List<LearningCandidate> getNextCandidateLearningNodes(
            NodeId currentNodeId,
            StudentId studentId,
            GraphVersion graphVersion
    ) {
        return candidates;
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