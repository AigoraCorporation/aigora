package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.application.context.OrchestrationContext;
import com.aigora.tutororchestrator.application.contracts.command.EvaluateLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.result.EvaluateLearningProgressResult;
import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import com.aigora.tutororchestrator.application.ports.StudentModelClient;
import com.aigora.tutororchestrator.domain.model.AssessmentSnapshot;
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
        this.studentModelClient = nonNull(studentModelClient, "StudentModelClient");
        this.assessmentClient = nonNull(assessmentClient, "AssessmentClient");
        this.completionPolicy = nonNull(completionPolicy, "CompletionPolicy");
        this.regressionPolicy = nonNull(regressionPolicy, "RegressionPolicy");
    }

    public EvaluateLearningProgressResult execute(
            EvaluateLearningProgressCommand command
    ) {
        nonNull(command, "EvaluateLearningProgressCommand");

        OrchestrationContext context = command.context();

        studentModelClient.getLearningState(context.studentId());

        AssessmentSnapshot assessment = assessmentClient.getAssessment(
                context.decisionEvidence().assessmentResultId()
        );

        validateAssessmentSnapshot(command, context, assessment);

        boolean completed = completionPolicy.isCompleted(assessment.mastered());

        boolean regressionRecommendedByStudentModel =
                studentModelClient.isRegressionRecommended(context.studentId());

        boolean regressionRecommended = regressionPolicy.shouldRegress(
                assessment.failed(),
                regressionRecommendedByStudentModel
        );

        return new EvaluateLearningProgressResult(
                context.studentId(),
                completed,
                regressionRecommended,
                reasonFor(completed, regressionRecommended)
        );
    }

    private void validateAssessmentSnapshot(
            EvaluateLearningProgressCommand command,
            OrchestrationContext context,
            AssessmentSnapshot assessment
    ) {
        if (assessment == null) {
            throw new IllegalStateException(
                    "AssessmentClient returned a null AssessmentSnapshot"
            );
        }

        if (!assessment.assessmentResultId().equals(
                context.decisionEvidence().assessmentResultId()
        )) {
            throw new IllegalStateException(
                    "AssessmentResultId does not match the orchestration context"
            );
        }

        if (!assessment.exerciseAttemptId().equals(
                context.sessionReference().exerciseAttemptId()
        )) {
            throw new IllegalStateException(
                    "ExerciseAttemptId does not match the orchestration context"
            );
        }

        if (!assessment.nodeId().equals(command.currentNodeId())) {
            throw new IllegalStateException(
                    "Assessment node does not match the current command node"
            );
        }
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
