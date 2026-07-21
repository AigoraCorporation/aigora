package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;

public record LearningCandidate(
        NodeId nodeId,
        CandidateClassification classification
) {
    public LearningCandidate {
        if (nodeId == null) {
            throw new IllegalArgumentException("NodeId must not be null");
        }
        if (classification == null) {
            throw new IllegalArgumentException("CandidateClassification must not be null");
        }
    }
}