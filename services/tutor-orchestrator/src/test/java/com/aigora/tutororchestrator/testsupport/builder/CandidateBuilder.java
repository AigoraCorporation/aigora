package com.aigora.tutororchestrator.testsupport.builder;

import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;

public final class CandidateBuilder {

    private NodeId nodeId = new NodeId("node-002");
    private CandidateClassification classification = CandidateClassification.NEXT_LEARNING;

    private CandidateBuilder() {
    }

    public static CandidateBuilder aCandidate() {
        return new CandidateBuilder();
    }

    public CandidateBuilder withNodeId(String nodeId) {
        this.nodeId = new NodeId(nodeId);
        return this;
    }

    public CandidateBuilder withClassification(CandidateClassification classification) {
        this.classification = classification;
        return this;
    }

    public LearningCandidate build() {
        return new LearningCandidate(nodeId, classification);
    }
}