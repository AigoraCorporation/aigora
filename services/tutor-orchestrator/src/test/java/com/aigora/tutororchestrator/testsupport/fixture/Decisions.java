package com.aigora.tutororchestrator.testsupport.fixture;

import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;

import static com.aigora.tutororchestrator.testsupport.builder.DecisionBuilder.aDecision;

public final class Decisions {
    public static final OrchestrationDecision SELECTED = aDecision().build();
    public static final OrchestrationDecision NO_CANDIDATE = aDecision().asNoCandidateAvailable().build();
    private Decisions() {}
}
