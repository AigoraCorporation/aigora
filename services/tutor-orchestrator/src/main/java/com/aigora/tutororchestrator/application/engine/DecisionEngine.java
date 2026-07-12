package com.aigora.tutororchestrator.application.engine;

import com.aigora.tutororchestrator.application.contracts.command.EvaluateLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectNextLearningNodeCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectRegressionNodeCommand;
import com.aigora.tutororchestrator.application.contracts.result.EvaluateLearningProgressResult;
import com.aigora.tutororchestrator.application.contracts.result.SelectNextLearningNodeResult;
import com.aigora.tutororchestrator.application.contracts.result.SelectRegressionNodeResult;
import com.aigora.tutororchestrator.application.usecase.EvaluateLearningProgressUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectNextLearningNodeUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectRegressionNodeUseCase;

/**
 * Application-level facade for deterministic orchestration operations.
 *
 * <p>The engine delegates each command to its corresponding use case.
 * It must not contain domain policies, ranking logic, selection logic,
 * infrastructure integration, or transport-specific behavior.</p>
 */
public final class DecisionEngine {

    private final SelectNextLearningNodeUseCase selectNextLearningNodeUseCase;
    private final SelectRegressionNodeUseCase selectRegressionNodeUseCase;
    private final EvaluateLearningProgressUseCase evaluateLearningProgressUseCase;

    public DecisionEngine(
            SelectNextLearningNodeUseCase selectNextLearningNodeUseCase,
            SelectRegressionNodeUseCase selectRegressionNodeUseCase,
            EvaluateLearningProgressUseCase evaluateLearningProgressUseCase
    ) {
        this.selectNextLearningNodeUseCase = requireNonNull(
                selectNextLearningNodeUseCase,
                "SelectNextLearningNodeUseCase must not be null"
        );

        this.selectRegressionNodeUseCase = requireNonNull(
                selectRegressionNodeUseCase,
                "SelectRegressionNodeUseCase must not be null"
        );

        this.evaluateLearningProgressUseCase = requireNonNull(
                evaluateLearningProgressUseCase,
                "EvaluateLearningProgressUseCase must not be null"
        );
    }

    /**
     * Delegates next-learning-node selection to its dedicated use case.
     */
    public SelectNextLearningNodeResult selectNextLearningNode(
            SelectNextLearningNodeCommand command
    ) {
        if (command == null) {
            throw new IllegalArgumentException(
                    "SelectNextLearningNodeCommand must not be null"
            );
        }

        return selectNextLearningNodeUseCase.execute(command);
    }

    /**
     * Delegates regression-node selection to its dedicated use case.
     */
    public SelectRegressionNodeResult selectRegressionNode(
            SelectRegressionNodeCommand command
    ) {
        if (command == null) {
            throw new IllegalArgumentException(
                    "SelectRegressionNodeCommand must not be null"
            );
        }

        return selectRegressionNodeUseCase.execute(command);
    }

    /**
     * Delegates learning-progress evaluation to its dedicated use case.
     */
    public EvaluateLearningProgressResult evaluateLearningProgress(
            EvaluateLearningProgressCommand command
    ) {
        if (command == null) {
            throw new IllegalArgumentException(
                    "EvaluateLearningProgressCommand must not be null"
            );
        }

        return evaluateLearningProgressUseCase.execute(command);
    }

    private static <T> T requireNonNull(T dependency, String message) {
        if (dependency == null) {
            throw new IllegalArgumentException(message);
        }

        return dependency;
    }
}