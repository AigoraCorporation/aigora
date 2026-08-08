package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.application.context.OrchestrationContext;
import com.aigora.tutororchestrator.application.contracts.command.SelectNextLearningNodeCommand;
import com.aigora.tutororchestrator.application.contracts.result.SelectNextLearningNodeResult;
import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import com.aigora.tutororchestrator.application.ports.CurriculumGraphClient;
import com.aigora.tutororchestrator.application.ports.StudentModelClient;
import com.aigora.tutororchestrator.domain.model.AssessmentSnapshot;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.policy.CompletionPolicy;
import com.aigora.tutororchestrator.domain.policy.EligibilityPolicy;
import com.aigora.tutororchestrator.domain.policy.RegressionPolicy;
import com.aigora.tutororchestrator.domain.ranking.DeterministicCandidateRanking;
import com.aigora.tutororchestrator.domain.selection.SelectionStrategy;

import java.util.List;

public final class SelectNextLearningNodeUseCase {

    private final CurriculumGraphClient curriculumGraphClient;
    private final StudentModelClient studentModelClient;
    private final AssessmentClient assessmentClient;
    private final EligibilityPolicy eligibilityPolicy;
    private final CompletionPolicy completionPolicy;
    private final RegressionPolicy regressionPolicy;
    private final DeterministicCandidateRanking candidateRanking;
    private final SelectionStrategy selectionStrategy;

    public SelectNextLearningNodeUseCase(
            CurriculumGraphClient curriculumGraphClient,
            StudentModelClient studentModelClient,
            AssessmentClient assessmentClient,
            EligibilityPolicy eligibilityPolicy,
            CompletionPolicy completionPolicy,
            RegressionPolicy regressionPolicy,
            DeterministicCandidateRanking candidateRanking,
            SelectionStrategy selectionStrategy
    ) {
        if (curriculumGraphClient == null) throw new IllegalArgumentException("CurriculumGraphClient must not be null");
        if (studentModelClient == null) throw new IllegalArgumentException("StudentModelClient must not be null");
        if (assessmentClient == null) throw new IllegalArgumentException("AssessmentClient must not be null");
        if (eligibilityPolicy == null) throw new IllegalArgumentException("EligibilityPolicy must not be null");
        if (completionPolicy == null) throw new IllegalArgumentException("CompletionPolicy must not be null");
        if (regressionPolicy == null) throw new IllegalArgumentException("RegressionPolicy must not be null");
        if (candidateRanking == null) throw new IllegalArgumentException("DeterministicCandidateRanking must not be null");
        if (selectionStrategy == null) throw new IllegalArgumentException("SelectionStrategy must not be null");

        this.curriculumGraphClient = curriculumGraphClient;
        this.studentModelClient = studentModelClient;
        this.assessmentClient = assessmentClient;
        this.eligibilityPolicy = eligibilityPolicy;
        this.completionPolicy = completionPolicy;
        this.regressionPolicy = regressionPolicy;
        this.candidateRanking = candidateRanking;
        this.selectionStrategy = selectionStrategy;
    }

    public SelectNextLearningNodeResult execute(
            SelectNextLearningNodeCommand command
    ) {
        if (command == null) {
            throw new IllegalArgumentException("SelectNextLearningNodeCommand must not be null");
        }

        OrchestrationContext context = command.context();

        StudentLearningState studentLearningState =
                studentModelClient.getLearningState(context.studentId());

        validateStudentModelSnapshot(context, studentLearningState);

        AssessmentSnapshot assessment = assessmentClient.getAssessment(
                context.decisionEvidence().assessmentResultId()
        );

        validateAssessmentSnapshot(command, context, assessment);

        boolean completedCurrentNode =
                completionPolicy.isCompleted(assessment.mastered());

        boolean regressionRecommended =
                studentLearningState.regressionRecommended();

        boolean shouldRegress = regressionPolicy.shouldRegress(
                assessment.failed(),
                regressionRecommended
        );

        if (!completedCurrentNode || shouldRegress) {
            return emptySelection(context);
        }

        List<LearningCandidate> candidates =
                curriculumGraphClient.getNextCandidateLearningNodes(
                        studentLearningState.currentNodeId(),
                        studentLearningState.studentId(),
                        studentLearningState.graphVersion()
                );

        List<LearningCandidate> eligibleCandidates = candidates.stream()
                .filter(candidate -> eligibilityPolicy.isEligible(studentLearningState, candidate))
                .filter(candidate -> !regressionPolicy.isRegressionCandidate(candidate))
                .toList();

        List<LearningCandidate> rankedCandidates =
                candidateRanking.rank(eligibleCandidates);

        return new SelectNextLearningNodeResult(
                selectionStrategy.select(
                        rankedCandidates,
                        context.studentId(),
                        context.decisionEvidence().graphVersion(),
                        context.traceContext().correlationId()
                )
        );
    }

    private SelectNextLearningNodeResult emptySelection(
            OrchestrationContext context
    ) {
        return new SelectNextLearningNodeResult(
                selectionStrategy.select(
                        List.of(),
                        context.studentId(),
                        context.decisionEvidence().graphVersion(),
                        context.traceContext().correlationId()
                )
        );
    }

    private void validateStudentModelSnapshot(
            OrchestrationContext context,
            StudentLearningState studentLearningState
    ) {
        if (studentLearningState == null) {
            throw new IllegalStateException(
                    "StudentModelClient returned a null StudentLearningState"
            );
        }

        if (!studentLearningState.studentId().equals(context.studentId())) {
            throw new IllegalStateException(
                    "StudentId does not match the orchestration context"
            );
        }

        if (!studentLearningState.studentModelVersion().equals(
                context.decisionEvidence().studentModelVersion()
        )) {
            throw new IllegalStateException(
                    "StudentModelVersion does not match the orchestration context"
            );
        }
    }

    private void validateAssessmentSnapshot(
            SelectNextLearningNodeCommand command,
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
}
