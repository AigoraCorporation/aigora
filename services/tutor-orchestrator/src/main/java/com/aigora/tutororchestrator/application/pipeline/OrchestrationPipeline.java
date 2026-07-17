package com.aigora.tutororchestrator.application.pipeline;

import com.aigora.tutororchestrator.application.contracts.command.EvaluateLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectNextLearningNodeCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectRegressionNodeCommand;
import com.aigora.tutororchestrator.application.contracts.result.EvaluateLearningProgressResult;
import com.aigora.tutororchestrator.application.contracts.result.OrchestrationPipelineResult;
import com.aigora.tutororchestrator.application.engine.DecisionEngine;

import static com.aigora.tutororchestrator.shared.validation.Require.nonNull;

/**
 * Coordinates the high-level deterministic orchestration lifecycle.
 *
 * <p>The pipeline evaluates progress first and routes the execution to
 * regression selection, next-node selection, or learning continuation.</p>
 */
public final class OrchestrationPipeline {

    private final DecisionEngine decisionEngine;

    public OrchestrationPipeline(
            DecisionEngine decisionEngine
    ) {
        this.decisionEngine = nonNull(
                decisionEngine,
                "DecisionEngine"
        );
    }

    public OrchestrationPipelineResult execute(
            EvaluateLearningProgressCommand command
    ) {
        nonNull(
                command,
                "EvaluateLearningProgressCommand"
        );

        EvaluateLearningProgressResult progress =
                decisionEngine.evaluateLearningProgress(command);

        if (progress.regressionRecommended()) {
            return executeRegressionFlow(
                    command,
                    progress
            );
        }

        if (progress.completed()) {
            return executeNextLearningNodeFlow(
                    command,
                    progress
            );
        }

        return OrchestrationPipelineResult.learningInProgress(
                progress
        );
    }

    private OrchestrationPipelineResult executeRegressionFlow(
            EvaluateLearningProgressCommand command,
            EvaluateLearningProgressResult progress
    ) {
        SelectRegressionNodeCommand regressionCommand =
                new SelectRegressionNodeCommand(
                        command.studentId(),
                        command.currentNodeId(),
                        command.graphVersion(),
                        command.correlationId()
                );

        var regressionResult =
                decisionEngine.selectRegressionNode(
                        regressionCommand
                );

        return OrchestrationPipelineResult.regressionNode(
                progress,
                regressionResult.decision()
        );
    }

    private OrchestrationPipelineResult executeNextLearningNodeFlow(
            EvaluateLearningProgressCommand command,
            EvaluateLearningProgressResult progress
    ) {
        SelectNextLearningNodeCommand nextNodeCommand =
                new SelectNextLearningNodeCommand(
                        command.studentId(),
                        command.currentNodeId(),
                        command.graphVersion(),
                        command.correlationId()
                );

        var nextNodeResult =
                decisionEngine.selectNextLearningNode(
                        nextNodeCommand
                );

        return OrchestrationPipelineResult.nextLearningNode(
                progress,
                nextNodeResult.decision()
        );
    }
}