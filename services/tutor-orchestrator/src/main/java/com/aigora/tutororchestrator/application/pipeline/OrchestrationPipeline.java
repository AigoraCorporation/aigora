package com.aigora.tutororchestrator.application.pipeline;

import com.aigora.tutororchestrator.application.contracts.command.EvaluateLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectNextLearningNodeCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectRegressionNodeCommand;
import com.aigora.tutororchestrator.application.contracts.result.EvaluateLearningProgressResult;
import com.aigora.tutororchestrator.application.contracts.result.OrchestrationPipelineResult;
import com.aigora.tutororchestrator.application.engine.DecisionEngine;
import com.aigora.tutororchestrator.application.ports.DecisionTraceSink;
import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;

import static com.aigora.tutororchestrator.shared.validation.Require.nonNull;

/**
 * Coordinates the high-level deterministic orchestration lifecycle.
 */
public final class OrchestrationPipeline {

    private final DecisionEngine decisionEngine;
    private final DecisionTraceSink decisionTraceSink;

    public OrchestrationPipeline(
            DecisionEngine decisionEngine,
            DecisionTraceSink decisionTraceSink
    ) {
        this.decisionEngine =
                nonNull(decisionEngine, "DecisionEngine");

        this.decisionTraceSink =
                nonNull(decisionTraceSink, "DecisionTraceSink");
    }

    public OrchestrationPipelineResult execute(
            EvaluateLearningProgressCommand command
    ) {
        nonNull(command, "EvaluateLearningProgressCommand");

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
                        command.context(),
                        command.currentNodeId()
                );

        var regressionResult =
                decisionEngine.selectRegressionNode(
                        regressionCommand
                );

        OrchestrationDecision decision =
                regressionResult.decision();

        recordDecision(decision);

        return OrchestrationPipelineResult.regressionNode(
                progress,
                decision
        );
    }

    private OrchestrationPipelineResult executeNextLearningNodeFlow(
            EvaluateLearningProgressCommand command,
            EvaluateLearningProgressResult progress
    ) {
        SelectNextLearningNodeCommand nextNodeCommand =
                new SelectNextLearningNodeCommand(
                        command.context(),
                        command.currentNodeId()
                );

        var nextNodeResult =
                decisionEngine.selectNextLearningNode(
                        nextNodeCommand
                );

        OrchestrationDecision decision =
                nextNodeResult.decision();

        recordDecision(decision);

        return OrchestrationPipelineResult.nextLearningNode(
                progress,
                decision
        );
    }

    private void recordDecision(
            OrchestrationDecision decision
    ) {
        decisionTraceSink.record(
                nonNull(decision, "OrchestrationDecision")
        );
    }
}