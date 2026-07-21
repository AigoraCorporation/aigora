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

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class OrchestrationPipelineResultTest {

    @Test
    void shouldCreateLearningInProgressResultWithoutDecision() {
        var progress = learningInProgress();

        var result = OrchestrationPipelineResult.learningInProgress(progress);

        assertEquals(progress, result.progress());
        assertEquals(
                OrchestrationRoute.LEARNING_IN_PROGRESS,
                result.route()
        );
        assertTrue(result.decision().isEmpty());
    }

    @Test
    void shouldCreateNextLearningNodeResultWithDecision() {
        var progress = learningCompleted();
        var decision = selectedDecision("node-002");

        var result = OrchestrationPipelineResult.nextLearningNode(
                progress,
                decision
        );

        assertEquals(progress, result.progress());
        assertEquals(
                OrchestrationRoute.NEXT_LEARNING_NODE,
                result.route()
        );
        assertEquals(decision, result.decision().orElseThrow());
    }

    @Test
    void shouldCreateRegressionNodeResultWithDecision() {
        var progress = regressionRecommended();
        var decision = selectedDecision("node-prerequisite-001");

        var result = OrchestrationPipelineResult.regressionNode(
                progress,
                decision
        );

        assertEquals(progress, result.progress());
        assertEquals(
                OrchestrationRoute.REGRESSION_NODE,
                result.route()
        );
        assertEquals(decision, result.decision().orElseThrow());
    }

    @Test
    void shouldRejectNullProgress() {
        assertThrows(
                NullPointerException.class,
                () -> new OrchestrationPipelineResult(
                        null,
                        OrchestrationRoute.LEARNING_IN_PROGRESS,
                        Optional.empty()
                )
        );
    }

    @Test
    void shouldRejectNullRoute() {
        assertThrows(
                NullPointerException.class,
                () -> new OrchestrationPipelineResult(
                        learningInProgress(),
                        null,
                        Optional.empty()
                )
        );
    }

    @Test
    void shouldRejectNullDecisionContainer() {
        assertThrows(
                NullPointerException.class,
                () -> new OrchestrationPipelineResult(
                        learningInProgress(),
                        OrchestrationRoute.LEARNING_IN_PROGRESS,
                        null
                )
        );
    }

    @Test
    void shouldRejectDecisionForLearningInProgressRoute() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationPipelineResult(
                        learningInProgress(),
                        OrchestrationRoute.LEARNING_IN_PROGRESS,
                        Optional.of(selectedDecision("node-002"))
                )
        );
    }

    @Test
    void shouldRejectMissingDecisionForNextLearningNodeRoute() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationPipelineResult(
                        learningCompleted(),
                        OrchestrationRoute.NEXT_LEARNING_NODE,
                        Optional.empty()
                )
        );
    }

    @Test
    void shouldRejectMissingDecisionForRegressionNodeRoute() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationPipelineResult(
                        regressionRecommended(),
                        OrchestrationRoute.REGRESSION_NODE,
                        Optional.empty()
                )
        );
    }

    @Test
    void shouldRejectNullDecisionInNextLearningNodeFactory() {
        assertThrows(
                NullPointerException.class,
                () -> OrchestrationPipelineResult.nextLearningNode(
                        learningCompleted(),
                        null
                )
        );
    }

    @Test
    void shouldRejectNullDecisionInRegressionNodeFactory() {
        assertThrows(
                NullPointerException.class,
                () -> OrchestrationPipelineResult.regressionNode(
                        regressionRecommended(),
                        null
                )
        );
    }

    @Test
    void shouldCompareByValue() {
        var progress = learningCompleted();
        var decision = selectedDecision("node-002");

        var first = OrchestrationPipelineResult.nextLearningNode(
                progress,
                decision
        );

        var second = OrchestrationPipelineResult.nextLearningNode(
                progress,
                decision
        );

        assertEquals(first, second);
    }

    private EvaluateLearningProgressResult learningCompleted() {
        return new EvaluateLearningProgressResult(
                new StudentId("student-001"),
                true,
                false,
                new DecisionReason(
                        "LEARNING_COMPLETED",
                        "Current learning node has been completed"
                )
        );
    }

    private EvaluateLearningProgressResult learningInProgress() {
        return new EvaluateLearningProgressResult(
                new StudentId("student-001"),
                false,
                false,
                new DecisionReason(
                        "LEARNING_IN_PROGRESS",
                        "Current learning node is still in progress"
                )
        );
    }

    private EvaluateLearningProgressResult regressionRecommended() {
        return new EvaluateLearningProgressResult(
                new StudentId("student-001"),
                false,
                true,
                new DecisionReason(
                        "REGRESSION_RECOMMENDED",
                        "Regression is recommended for the current learning state"
                )
        );
    }

    private OrchestrationDecision selectedDecision(String nodeId) {
        return new OrchestrationDecision(
                new DecisionId("decision-001"),
                new StudentId("student-001"),
                new NodeId(nodeId),
                DecisionStatus.SELECTED,
                new DecisionReason(
                        "CANDIDATE_SELECTED",
                        "The highest-ranked candidate was selected"
                ),
                new GraphVersion("v1.0.0"),
                new CorrelationId("corr-001")
        );
    }
}