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

class SelectRegressionNodeResultTest {

    @Test
    void shouldCreateResult() {
        var decision = regressionDecision();

        var result = new SelectRegressionNodeResult(decision);

        assertEquals(decision, result.decision());
    }

    @Test
    void shouldCompareByValue() {
        var decision = regressionDecision();

        assertEquals(
                new SelectRegressionNodeResult(decision),
                new SelectRegressionNodeResult(decision)
        );
    }

    @Test
    void shouldRejectNullDecision() {
        assertThrows(IllegalArgumentException.class, () ->
                new SelectRegressionNodeResult(null)
        );
    }

    private OrchestrationDecision regressionDecision() {
        return aDecision()
                .withSelectedNodeId("node-prerequisite-001")
                .build();
    }
}