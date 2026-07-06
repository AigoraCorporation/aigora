package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.application.contracts.command.EvaluateLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.result.EvaluateLearningProgressResult;
import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import com.aigora.tutororchestrator.application.ports.StudentModelClient;
import com.aigora.tutororchestrator.domain.model.DecisionReason;
import com.aigora.tutororchestrator.domain.policy.CompletionPolicy;
import com.aigora.tutororchestrator.domain.policy.RegressionPolicy;

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
        if (studentModelClient == null) {
            throw new IllegalArgumentException("StudentModelClient must not be null");
        }
        if (assessmentClient == null) {
            throw new IllegalArgumentException("AssessmentClient must not be null");
        }
        if (completionPolicy == null) {
            throw new IllegalArgumentException("CompletionPolicy must not be null");
        }
        if (regressionPolicy == null) {
            throw new IllegalArgumentException("RegressionPolicy must not be null");
        }

        this.studentModelClient = studentModelClient;
        this.assessmentClient = assessmentClient;
        this.completionPolicy = completionPolicy;
        this.regressionPolicy = regressionPolicy;
    }

    public EvaluateLearningProgressResult execute(EvaluateLearningProgressCommand command) {
        if (command == null) {
            throw new IllegalArgumentException("EvaluateLearningProgressCommand must not be null");
        }

        studentModelClient.getLearningState(command.studentId());

        boolean masteredCurrentNode = assessmentClient.hasMasteredNode(
                command.studentId(),
                command.currentNodeId()
        );

        boolean completed = completionPolicy.isCompleted(masteredCurrentNode);

        boolean failedCurrentNode = assessmentClient.hasFailedNode(
                command.studentId(),
                command.currentNodeId()
        );

        boolean regressionRecommendedByStudentModel =
                studentModelClient.isRegressionRecommended(command.studentId());

        boolean regressionRecommended = regressionPolicy.shouldRegress(
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
                    "REGRESSION_RECOMMENDED",
                    "Regression is recommended for the current learning state"
            );
        }

        if (completed) {
            return new DecisionReason(
                    "LEARNING_COMPLETED",
                    "Current learning node has been completed"
            );
        }

        return new DecisionReason(
                "LEARNING_IN_PROGRESS",
                "Current learning node is still in progress"
        );
    }
}