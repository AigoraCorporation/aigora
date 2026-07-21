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

import static com.aigora.tutororchestrator.shared.validation.Require.nonNull;

/**
 * Application-level facade for deterministic orchestration operations.
 *
 * <p>The engine delegates each command to its corresponding use case.
 * It contains no policy, ranking, selection, transport, or infrastructure
 * behavior.</p>
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
        this.selectNextLearningNodeUseCase = nonNull(
                selectNextLearningNodeUseCase,
                "SelectNextLearningNodeUseCase"
        );

        this.selectRegressionNodeUseCase = nonNull(
                selectRegressionNodeUseCase,
                "SelectRegressionNodeUseCase"
        );

        this.evaluateLearningProgressUseCase = nonNull(
                evaluateLearningProgressUseCase,
                "EvaluateLearningProgressUseCase"
        );
    }

    public SelectNextLearningNodeResult selectNextLearningNode(
            SelectNextLearningNodeCommand command
    ) {
        return selectNextLearningNodeUseCase.execute(
                nonNull(
                        command,
                        "SelectNextLearningNodeCommand"
                )
        );
    }

    public SelectRegressionNodeResult selectRegressionNode(
            SelectRegressionNodeCommand command
    ) {
        return selectRegressionNodeUseCase.execute(
                nonNull(
                        command,
                        "SelectRegressionNodeCommand"
                )
        );
    }

    public EvaluateLearningProgressResult evaluateLearningProgress(
            EvaluateLearningProgressCommand command
    ) {
        return evaluateLearningProgressUseCase.execute(
                nonNull(
                        command,
                        "EvaluateLearningProgressCommand"
                )
        );
    }
}