package com.aigora.tutororchestrator.domain.model;

import com.aigora.tutororchestrator.domain.valueobjects.DecisionId;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

public record OrchestrationDecision(
        DecisionId decisionId,
        StudentId studentId,
        NodeId selectedNodeId,
        DecisionStatus status,
        DecisionReason reason,
        DecisionTrace trace
) {

    public OrchestrationDecision {
        if (decisionId == null) {
            throw new IllegalArgumentException(
                    "DecisionId must not be null"
            );
        }

        if (studentId == null) {
            throw new IllegalArgumentException(
                    "StudentId must not be null"
            );
        }

        if (status == null) {
            throw new IllegalArgumentException(
                    "DecisionStatus must not be null"
            );
        }

        if (reason == null) {
            throw new IllegalArgumentException(
                    "DecisionReason must not be null"
            );
        }

        if (trace == null) {
            throw new IllegalArgumentException(
                    "DecisionTrace must not be null"
            );
        }

        if (status == DecisionStatus.SELECTED
                && selectedNodeId == null) {
            throw new IllegalArgumentException(
                    "Selected decisions must have a selected node"
            );
        }
    }

}
