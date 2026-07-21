package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.application.contracts.command.EvaluateLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.result.EvaluateLearningProgressResult;
import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import com.aigora.tutororchestrator.application.ports.StudentModelClient;
import com.aigora.tutororchestrator.domain.model.DecisionReason;
import com.aigora.tutororchestrator.domain.model.DecisionReasonCode;
import com.aigora.tutororchestrator.domain.policy.CompletionPolicy;
import com.aigora.tutororchestrator.domain.policy.RegressionPolicy;

import static com.aigora.tutororchestrator.shared.validation.Require.nonNull;

public final class EvaluateLearningProgressUseCase {

    private final StudentModelClient studentModelClient;
    private final AssessmentClient assessmentClient;
    private final CompletionPolicy completionPolicy;
    private final RegressionPolicy regressionPolicy;

    public EvaluateLearningProgressUseCase(
            StudentModelClient studentModelClient,
            AssessmentClient assessmentClient,
            CompletionPolicy completionPolicy,
            RegressionPolicy regressionPolicy
    ) {
        this.studentModelClient = nonNull(
                studentModelClient,
                "StudentModelClient"
        );

        this.assessmentClient = nonNull(
                assessmentClient,
                "AssessmentClient"
        );

        this.completionPolicy = nonNull(
                completionPolicy,
                "CompletionPolicy"
        );

        this.regressionPolicy = nonNull(
                regressionPolicy,
                "RegressionPolicy"
        );
    }

    public EvaluateLearningProgressResult execute(
            EvaluateLearningProgressCommand command
    ) {
        nonNull(command, "EvaluateLearningProgressCommand");

        studentModelClient.getLearningState(command.studentId());

        boolean masteredCurrentNode = assessmentClient.hasMasteredNode(
                command.studentId(),
                command.currentNodeId()
        );

        boolean completed =
                completionPolicy.isCompleted(masteredCurrentNode);

        boolean failedCurrentNode = assessmentClient.hasFailedNode(
                command.studentId(),
                command.currentNodeId()
        );

        boolean regressionRecommendedByStudentModel =
                studentModelClient.isRegressionRecommended(
                        command.studentId()
                );

        boolean regressionRecommended =
                regressionPolicy.shouldRegress(
                        failedCurrentNode,
                        regressionRecommendedByStudentModel
                );

        return new EvaluateLearningProgressResult(
                command.studentId(),
                completed,
                regressionRecommended,
                reasonFor(completed, regressionRecommended)
        );
    }

    private DecisionReason reasonFor(
            boolean completed,
            boolean regressionRecommended
    ) {
        if (regressionRecommended) {
            return new DecisionReason(
                    DecisionReasonCode.REGRESSION_RECOMMENDED,
                    "Regression is recommended for the current learning state"
            );
        }

        if (completed) {
            return new DecisionReason(
                    DecisionReasonCode.LEARNING_COMPLETED,
                    "Current learning node has been completed"
            );
        }

        return new DecisionReason(
                DecisionReasonCode.LEARNING_IN_PROGRESS,
                "Current learning node is still in progress"
        );
    }
}