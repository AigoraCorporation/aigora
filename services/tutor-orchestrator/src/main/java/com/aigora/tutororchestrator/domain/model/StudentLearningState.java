package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.valueobjects.*;

public record StudentLearningState(
        StudentId studentId,
        NodeId currentNodeId,
        GraphVersion graphVersion
) {
    public StudentLearningState {
        if (studentId == null) {
            throw new IllegalArgumentException("StudentId must not be null");
        }
        if (currentNodeId == null) {
            throw new IllegalArgumentException("CurrentNodeId must not be null");
        }
        if (graphVersion == null) {
            throw new IllegalArgumentException("GraphVersion must not be null");
        }
    }
}