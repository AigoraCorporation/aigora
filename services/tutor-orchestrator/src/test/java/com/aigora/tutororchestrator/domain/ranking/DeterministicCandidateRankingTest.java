package com.aigora.tutororchestrator.domain.ranking;

import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class DeterministicCandidateRankingTest {

    private final DeterministicCandidateRanking ranking = new DeterministicCandidateRanking();

    @Test
    void shouldRankCandidatesByClassificationPriority() {
        var candidates = List.of(
                candidate("node-004", CandidateClassification.REGRESSION),
                candidate("node-002", CandidateClassification.REINFORCEMENT),
                candidate("node-003", CandidateClassification.REVIEW),
                candidate("node-001", CandidateClassification.NEXT_LEARNING)
        );

        var ranked = ranking.rank(candidates);

        assertEquals(candidate("node-001", CandidateClassification.NEXT_LEARNING), ranked.get(0));
        assertEquals(candidate("node-002", CandidateClassification.REINFORCEMENT), ranked.get(1));
        assertEquals(candidate("node-003", CandidateClassification.REVIEW), ranked.get(2));
        assertEquals(candidate("node-004", CandidateClassification.REGRESSION), ranked.get(3));
    }

    @Test
    void shouldApplyLexicographicalTieBreakByNodeId() {
        var candidates = List.of(
                candidate("node-003", CandidateClassification.NEXT_LEARNING),
                candidate("node-001", CandidateClassification.NEXT_LEARNING),
                candidate("node-002", CandidateClassification.NEXT_LEARNING)
        );

        var ranked = ranking.rank(candidates);

        assertEquals(new NodeId("node-001"), ranked.get(0).nodeId());
        assertEquals(new NodeId("node-002"), ranked.get(1).nodeId());
        assertEquals(new NodeId("node-003"), ranked.get(2).nodeId());
    }

    @Test
    void shouldBeDeterministicForSameInput() {
        var candidates = List.of(
                candidate("node-003", CandidateClassification.REVIEW),
                candidate("node-001", CandidateClassification.NEXT_LEARNING),
                candidate("node-002", CandidateClassification.REINFORCEMENT)
        );

        var firstRanking = ranking.rank(candidates);
        var secondRanking = ranking.rank(candidates);

        assertEquals(firstRanking, secondRanking);
    }

    @Test
    void shouldReturnEmptyListWhenCandidatesAreEmpty() {
        var ranked = ranking.rank(List.of());

        assertTrue(ranked.isEmpty());
    }

    @Test
    void shouldReturnSingleCandidateList() {
        var candidate = candidate("node-001", CandidateClassification.NEXT_LEARNING);

        var ranked = ranking.rank(List.of(candidate));

        assertEquals(List.of(candidate), ranked);
    }

    @Test
    void shouldNotMutateInputList() {
        var candidates = List.of(
                candidate("node-003", CandidateClassification.REVIEW),
                candidate("node-001", CandidateClassification.NEXT_LEARNING),
                candidate("node-002", CandidateClassification.REINFORCEMENT)
        );

        var original = List.copyOf(candidates);

        ranking.rank(candidates);

        assertEquals(original, candidates);
    }

    @Test
    void shouldRejectNullCandidateList() {
        assertThrows(IllegalArgumentException.class, () ->
                ranking.rank(null)
        );
    }

    private LearningCandidate candidate(
            String nodeId,
            CandidateClassification classification
    ) {
        return new LearningCandidate(
                new NodeId(nodeId),
                classification
        );
    }
}