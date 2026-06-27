package com.aigora.tutororchestrator.application.ports;

import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

import java.util.List;

public interface CurriculumGraphClient {

    NodeId getCurrentLearningNode(StudentId studentId, GraphVersion graphVersion);

    List<NodeId> getPrerequisites(NodeId nodeId, GraphVersion graphVersion);

    List<LearningCandidate> getNextCandidateLearningNodes(
            NodeId currentNodeId,
            StudentId studentId,
            GraphVersion graphVersion
    );

    List<NodeId> getUnlockedNodes(StudentId studentId, GraphVersion graphVersion);

    boolean nodeExists(NodeId nodeId, GraphVersion graphVersion);
}