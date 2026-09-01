package com.aigora.tutororchestrator.domain.model;

import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;

public record StudentLearningState(
        StudentId studentId,
        NodeId currentNodeId,
        GraphVersion graphVersion,
        StudentModelVersion studentModelVersion,
        boolean currentNodeCompleted,
        boolean regressionRecommended
) {

    public StudentLearningState {
        if (studentId == null) {
            throw new IllegalArgumentException(
                    "StudentId must not be null"
            );
        }

        if (currentNodeId == null) {
            throw new IllegalArgumentException(
                    "NodeId must not be null"
            );
        }

        if (graphVersion == null) {
            throw new IllegalArgumentException(
                    "GraphVersion must not be null"
            );
        }

        if (studentModelVersion == null) {
            throw new IllegalArgumentException(
                    "StudentModelVersion must not be null"
            );
        }
    }
}