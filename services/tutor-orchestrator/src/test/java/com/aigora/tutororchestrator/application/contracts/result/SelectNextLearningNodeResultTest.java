package com.aigora.tutororchestrator.application.contracts.result;

import com.aigora.tutororchestrator.domain.model.DecisionReason;
import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;
import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.DecisionId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import org.junit.jupiter.api.Test;

import static com.aigora.tutororchestrator.testsupport.builder.DecisionBuilder.aDecision;
import static org.junit.jupiter.api.Assertions.*;

class SelectNextLearningNodeResultTest {

    @Test
    void shouldCreateResult() {
        var decision = selectedDecision();

        var result = new SelectNextLearningNodeResult(decision);

        assertEquals(decision, result.decision());
    }

    @Test
    void shouldCompareByValue() {
        var decision = selectedDecision();

        assertEquals(
                new SelectNextLearningNodeResult(decision),
                new SelectNextLearningNodeResult(decision)
        );
    }

    @Test
    void shouldRejectNullDecision() {
        assertThrows(IllegalArgumentException.class, () ->
                new SelectNextLearningNodeResult(null)
        );
    }

    private OrchestrationDecision selectedDecision() {
        return aDecision()
                .withSelectedNodeId("node-001")
                .build();
    }
}