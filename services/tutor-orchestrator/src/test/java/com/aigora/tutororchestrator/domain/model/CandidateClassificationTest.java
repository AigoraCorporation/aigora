package com.aigora.tutororchestrator.domain.model;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class CandidateClassificationTest {

    @Test
    void shouldContainExpectedCandidateClassifications() {
        assertNotNull(CandidateClassification.NEXT_LEARNING);
        assertNotNull(CandidateClassification.REVIEW);
        assertNotNull(CandidateClassification.REGRESSION);
        assertNotNull(CandidateClassification.REINFORCEMENT);
    }
}