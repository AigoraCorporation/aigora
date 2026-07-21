package com.aigora.tutororchestrator.application.configuration;

import com.aigora.tutororchestrator.application.engine.DecisionEngine;
import com.aigora.tutororchestrator.application.pipeline.OrchestrationPipeline;
import com.aigora.tutororchestrator.application.usecase.EvaluateLearningProgressUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectNextLearningNodeUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectRegressionNodeUseCase;

import static com.aigora.tutororchestrator.shared.validation.Require.nonNull;

/**
 * Immutable application configuration produced by the composition root.
 */
public record TutorOrchestratorConfiguration(
        SelectNextLearningNodeUseCase selectNextLearningNodeUseCase,
        SelectRegressionNodeUseCase selectRegressionNodeUseCase,
        EvaluateLearningProgressUseCase evaluateLearningProgressUseCase,
        DecisionEngine decisionEngine,
        OrchestrationPipeline orchestrationPipeline
) implements TutorOrchestratorFactory {

    public TutorOrchestratorConfiguration {
        selectNextLearningNodeUseCase = nonNull(
                selectNextLearningNodeUseCase,
                "SelectNextLearningNodeUseCase"
        );

        selectRegressionNodeUseCase = nonNull(
                selectRegressionNodeUseCase,
                "SelectRegressionNodeUseCase"
        );

        evaluateLearningProgressUseCase = nonNull(
                evaluateLearningProgressUseCase,
                "EvaluateLearningProgressUseCase"
        );

        decisionEngine = nonNull(
                decisionEngine,
                "DecisionEngine"
        );

        orchestrationPipeline = nonNull(
                orchestrationPipeline,
                "OrchestrationPipeline"
        );
    }
}