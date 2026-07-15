package com.aigora.tutororchestrator.application.pipeline;

import com.aigora.tutororchestrator.application.contracts.command.EvaluateLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectNextLearningNodeCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectRegressionNodeCommand;
import com.aigora.tutororchestrator.application.contracts.result.EvaluateLearningProgressResult;
import com.aigora.tutororchestrator.application.contracts.result.OrchestrationPipelineResult;
import com.aigora.tutororchestrator.application.engine.DecisionEngine;

/**
 * Coordinates the high-level deterministic orchestration lifecycle.
 *
 * <p>The pipeline evaluates learning progress first and then routes execution
 * to regression selection, next-node selection, or learning continuation.</p>
 *
 * <p>This component contains no policy, ranking, selection, transport, or
 * infrastructure logic.</p>
 */
public final class OrchestrationPipeline {

    private final DecisionEngine decisionEngine;

    public OrchestrationPipeline(DecisionEngine decisionEngine) {
        if (decisionEngine == null) {
            throw new IllegalArgumentException(
                    "DecisionEngine must not be null"
            );
        }

        this.decisionEngine = decisionEngine;
    }

    public OrchestrationPipelineResult execute(
            EvaluateLearningProgressCommand command
    ) {
        if (command == null) {
            throw new IllegalArgumentException(
                    "EvaluateLearningProgressCommand must not be null"
            );
        }

        EvaluateLearningProgressResult progress =
                decisionEngine.evaluateLearningProgress(command);

        if (progress.regressionRecommended()) {
            return executeRegressionFlow(command, progress);
        }

        if (progress.completed()) {
            return executeNextLearningNodeFlow(command, progress);
        }

        return OrchestrationPipelineResult.learningInProgress(progress);
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
                decisionEngine.selectRegressionNode(regressionCommand);

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
                decisionEngine.selectNextLearningNode(nextNodeCommand);

        return OrchestrationPipelineResult.nextLearningNode(
                progress,
                nextNodeResult.decision()
        );
    }
}