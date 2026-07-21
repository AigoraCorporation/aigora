package com.aigora.tutororchestrator.testsupport.fixture;

import com.aigora.tutororchestrator.domain.model.DecisionReason;
import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;
import com.aigora.tutororchestrator.domain.valueobjects.DecisionId;

public final class Decisions {

    public static final OrchestrationDecision SELECTED =
            new OrchestrationDecision(
                    new DecisionId("decision-001"),
                    Students.STUDENT_001,
                    Nodes.NEXT_NODE,
                    DecisionStatus.SELECTED,
                    new DecisionReason("CANDIDATE_SELECTED", "The highest-ranked candidate was selected"),
                    GraphVersions.DEFAULT,
                    CorrelationIds.DEFAULT
            );

    public static final OrchestrationDecision NO_CANDIDATE =
            new OrchestrationDecision(
                    new DecisionId("decision-002"),
                    Students.STUDENT_001,
                    null,
                    DecisionStatus.NO_CANDIDATE_AVAILABLE,
                    new DecisionReason("NO_CANDIDATE_AVAILABLE", "No ranked candidates were available for selection"),
                    GraphVersions.DEFAULT,
                    CorrelationIds.DEFAULT
            );

    private Decisions() {
    }
}