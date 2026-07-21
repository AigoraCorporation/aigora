package com.aigora.tutororchestrator.application.contracts.result;

import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;

import java.util.Objects;
import java.util.Optional;

/**
 * Application-safe result produced by the orchestration pipeline.
 *
 * <p>A decision is present only when the pipeline routes execution to
 * next-node or regression-node selection.</p>
 */
public record OrchestrationPipelineResult(
        EvaluateLearningProgressResult progress,
        OrchestrationRoute route,
        Optional<OrchestrationDecision> decision
) {

    public OrchestrationPipelineResult {
        Objects.requireNonNull(
                progress,
                "EvaluateLearningProgressResult must not be null"
        );

        Objects.requireNonNull(
                route,
                "OrchestrationRoute must not be null"
        );

        Objects.requireNonNull(
                decision,
                "Decision must not be null"
        );

        validateDecisionForRoute(route, decision);
    }

    public static OrchestrationPipelineResult learningInProgress(
            EvaluateLearningProgressResult progress
    ) {
        return new OrchestrationPipelineResult(
                progress,
                OrchestrationRoute.LEARNING_IN_PROGRESS,
                Optional.empty()
        );
    }

    public static OrchestrationPipelineResult nextLearningNode(
            EvaluateLearningProgressResult progress,
            OrchestrationDecision decision
    ) {
        return new OrchestrationPipelineResult(
                progress,
                OrchestrationRoute.NEXT_LEARNING_NODE,
                Optional.of(
                        Objects.requireNonNull(
                                decision,
                                "OrchestrationDecision must not be null"
                        )
                )
        );
    }

    public static OrchestrationPipelineResult regressionNode(
            EvaluateLearningProgressResult progress,
            OrchestrationDecision decision
    ) {
        return new OrchestrationPipelineResult(
                progress,
                OrchestrationRoute.REGRESSION_NODE,
                Optional.of(
                        Objects.requireNonNull(
                                decision,
                                "OrchestrationDecision must not be null"
                        )
                )
        );
    }

    private static void validateDecisionForRoute(
            OrchestrationRoute route,
            Optional<OrchestrationDecision> decision
    ) {
        if (route == OrchestrationRoute.LEARNING_IN_PROGRESS
                && decision.isPresent()) {
            throw new IllegalArgumentException(
                    "Learning-in-progress result must not contain a decision"
            );
        }

        if (route != OrchestrationRoute.LEARNING_IN_PROGRESS
                && decision.isEmpty()) {
            throw new IllegalArgumentException(
                    "Node-selection result must contain a decision"
            );
        }
    }
}