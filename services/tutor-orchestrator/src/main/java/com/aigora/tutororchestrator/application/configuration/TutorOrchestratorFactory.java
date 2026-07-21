package com.aigora.tutororchestrator.application.configuration;

import com.aigora.tutororchestrator.application.engine.DecisionEngine;
import com.aigora.tutororchestrator.application.pipeline.OrchestrationPipeline;
import com.aigora.tutororchestrator.application.usecase.EvaluateLearningProgressUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectNextLearningNodeUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectRegressionNodeUseCase;

/**
 * Exposes the application components assembled by the Tutor Orchestrator
 * composition root.
 *
 * <p>This contract is framework-independent and must not depend on Spring,
 * CDI, Guice, gRPC, HTTP, or infrastructure-specific implementations.</p>
 */
public interface TutorOrchestratorFactory {

    SelectNextLearningNodeUseCase selectNextLearningNodeUseCase();

    SelectRegressionNodeUseCase selectRegressionNodeUseCase();

    EvaluateLearningProgressUseCase evaluateLearningProgressUseCase();

    DecisionEngine decisionEngine();

    OrchestrationPipeline orchestrationPipeline();
}