package com.aigora.tutororchestrator.application.configuration;

import com.aigora.tutororchestrator.application.engine.DecisionEngine;
import com.aigora.tutororchestrator.application.pipeline.OrchestrationPipeline;
import com.aigora.tutororchestrator.application.usecase.EvaluateLearningProgressUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectNextLearningNodeUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectRegressionNodeUseCase;

import java.util.Objects;

/**
 * Immutable application configuration produced by the Tutor Orchestrator
 * composition root.
 */
public record TutorOrchestratorConfiguration(
        SelectNextLearningNodeUseCase selectNextLearningNodeUseCase,
        SelectRegressionNodeUseCase selectRegressionNodeUseCase,
        EvaluateLearningProgressUseCase evaluateLearningProgressUseCase,
        DecisionEngine decisionEngine,
        OrchestrationPipeline orchestrationPipeline
) implements TutorOrchestratorFactory {

    public TutorOrchestratorConfiguration {
        Objects.requireNonNull(
                selectNextLearningNodeUseCase,
                "SelectNextLearningNodeUseCase must not be null"
        );

        Objects.requireNonNull(
                selectRegressionNodeUseCase,
                "SelectRegressionNodeUseCase must not be null"
        );

        Objects.requireNonNull(
                evaluateLearningProgressUseCase,
                "EvaluateLearningProgressUseCase must not be null"
        );

        Objects.requireNonNull(
                decisionEngine,
                "DecisionEngine must not be null"
        );

        Objects.requireNonNull(
                orchestrationPipeline,
                "OrchestrationPipeline must not be null"
        );
    }
}