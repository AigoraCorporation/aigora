package com.aigora.tutororchestrator.application.ports;

import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

public interface AssessmentClient {

    boolean hasMasteredNode(StudentId studentId, NodeId nodeId);

    boolean hasFailedNode(StudentId studentId, NodeId nodeId);
}