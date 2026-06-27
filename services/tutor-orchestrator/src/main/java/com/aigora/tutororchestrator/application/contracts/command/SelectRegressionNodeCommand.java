package com.aigora.tutororchestrator.application.contracts.command;

import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

public record SelectRegressionNodeCommand(
        StudentId studentId,
        NodeId currentNodeId,
        GraphVersion graphVersion,
        CorrelationId correlationId
) {
    public SelectRegressionNodeCommand {
        if (studentId == null) throw new IllegalArgumentException("StudentId must not be null");
        if (currentNodeId == null) throw new IllegalArgumentException("CurrentNodeId must not be null");
        if (graphVersion == null) throw new IllegalArgumentException("GraphVersion must not be null");
        if (correlationId == null) throw new IllegalArgumentException("CorrelationId must not be null");
    }
}