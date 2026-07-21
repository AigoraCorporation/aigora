package com.aigora.tutororchestrator.domain.ranking;

import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;

import java.util.Comparator;
import java.util.List;

public final class DeterministicCandidateRanking {

    public List<LearningCandidate> rank(List<LearningCandidate> candidates) {
        if (candidates == null) {
            throw new IllegalArgumentException("Candidates must not be null");
        }

        return candidates.stream()
                .sorted(candidateComparator())
                .toList();
    }

    private Comparator<LearningCandidate> candidateComparator() {
        return Comparator
                .comparingInt((LearningCandidate candidate) ->
                        classificationPriority(candidate.classification())
                )
                .thenComparing(candidate -> candidate.nodeId().value());
    }

    private int classificationPriority(CandidateClassification classification) {
        if (classification == null) {
            throw new IllegalArgumentException("CandidateClassification must not be null");
        }

        return switch (classification) {
            case NEXT_LEARNING -> 1;
            case REINFORCEMENT -> 2;
            case REVIEW -> 3;
            case REGRESSION -> 4;
        };
    }
}