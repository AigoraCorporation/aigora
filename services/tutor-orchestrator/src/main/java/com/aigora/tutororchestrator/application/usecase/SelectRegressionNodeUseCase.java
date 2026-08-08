package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.application.context.OrchestrationContext;
import com.aigora.tutororchestrator.application.contracts.command.SelectRegressionNodeCommand;
import com.aigora.tutororchestrator.application.contracts.result.SelectRegressionNodeResult;
import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import com.aigora.tutororchestrator.application.ports.CurriculumGraphClient;
import com.aigora.tutororchestrator.application.ports.StudentModelClient;
import com.aigora.tutororchestrator.domain.model.AssessmentSnapshot;
import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.model.StudentLearningState;
import com.aigora.tutororchestrator.domain.policy.RegressionPolicy;
import com.aigora.tutororchestrator.domain.ranking.DeterministicCandidateRanking;
import com.aigora.tutororchestrator.domain.selection.SelectionStrategy;

import java.util.List;

public final class SelectRegressionNodeUseCase {

    private final CurriculumGraphClient curriculumGraphClient;
    private final StudentModelClient studentModelClient;
    private final AssessmentClient assessmentClient;
    private final RegressionPolicy regressionPolicy;
    private final DeterministicCandidateRanking candidateRanking;
    private final SelectionStrategy selectionStrategy;

    public SelectRegressionNodeUseCase(
            CurriculumGraphClient curriculumGraphClient,
            StudentModelClient studentModelClient,
            AssessmentClient assessmentClient,
            RegressionPolicy regressionPolicy,
            DeterministicCandidateRanking candidateRanking,
            SelectionStrategy selectionStrategy
    ) {
        if (curriculumGraphClient == null) {
            throw new IllegalArgumentException(
                    "CurriculumGraphClient must not be null"
            );
        }

        if (studentModelClient == null) {
            throw new IllegalArgumentException(
                    "StudentModelClient must not be null"
            );
        }

        if (assessmentClient == null) {
            throw new IllegalArgumentException(
                    "AssessmentClient must not be null"
            );
        }

        if (regressionPolicy == null) {
            throw new IllegalArgumentException(
                    "RegressionPolicy must not be null"
            );
        }

        if (candidateRanking == null) {
            throw new IllegalArgumentException(
                    "DeterministicCandidateRanking must not be null"
            );
        }

        if (selectionStrategy == null) {
            throw new IllegalArgumentException(
                    "SelectionStrategy must not be null"
            );
        }

        this.curriculumGraphClient = curriculumGraphClient;
        this.studentModelClient = studentModelClient;
        this.assessmentClient = assessmentClient;
        this.regressionPolicy = regressionPolicy;
        this.candidateRanking = candidateRanking;
        this.selectionStrategy = selectionStrategy;
    }

    public SelectRegressionNodeResult execute(
            SelectRegressionNodeCommand command
    ) {
        if (command == null) {
            throw new IllegalArgumentException(
                    "SelectRegressionNodeCommand must not be null"
            );
        }

        OrchestrationContext context = command.context();

        StudentLearningState studentLearningState =
                studentModelClient.getLearningState(context.studentId());

        validateStudentModelSnapshot(context, studentLearningState);

        AssessmentSnapshot assessmentSnapshot =
                assessmentClient.getAssessment(
                        context.decisionEvidence().assessmentResultId()
                );

        validateAssessmentSnapshot(
                command,
                context,
                assessmentSnapshot
        );

        boolean regressionRecommended =
                studentLearningState.regressionRecommended();

        boolean shouldRegress = regressionPolicy.shouldRegress(
                assessmentSnapshot.failed(),
                regressionRecommended
        );

        if (!shouldRegress) {
            return emptySelection(context);
        }

        List<LearningCandidate> regressionCandidates =
                curriculumGraphClient.getPrerequisites(
                                studentLearningState.currentNodeId(),
                                studentLearningState.graphVersion()
                        )
                        .stream()
                        .map(nodeId -> new LearningCandidate(
                                nodeId,
                                CandidateClassification.REGRESSION
                        ))
                        .filter(regressionPolicy::isRegressionCandidate)
                        .toList();

        List<LearningCandidate> rankedCandidates =
                candidateRanking.rank(regressionCandidates);

        return new SelectRegressionNodeResult(
                selectionStrategy.select(
                        rankedCandidates,
                        context.studentId(),
                        context.decisionEvidence().graphVersion(),
                        context.traceContext().correlationId()
                )
        );
    }

    private SelectRegressionNodeResult emptySelection(
            OrchestrationContext context
    ) {
        return new SelectRegressionNodeResult(
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
            SelectRegressionNodeCommand command,
            OrchestrationContext context,
            AssessmentSnapshot assessmentSnapshot
    ) {
        if (assessmentSnapshot == null) {
            throw new IllegalStateException(
                    "AssessmentClient returned a null AssessmentSnapshot"
            );
        }

        if (!assessmentSnapshot.assessmentResultId().equals(
                context.decisionEvidence().assessmentResultId()
        )) {
            throw new IllegalStateException(
                    "AssessmentResultId does not match the orchestration context"
            );
        }

        if (!assessmentSnapshot.exerciseAttemptId().equals(
                context.sessionReference().exerciseAttemptId()
        )) {
            throw new IllegalStateException(
                    "ExerciseAttemptId does not match the orchestration context"
            );
        }

        if (!assessmentSnapshot.nodeId().equals(command.currentNodeId())) {
            throw new IllegalStateException(
                    "Assessment node does not match the current command node"
            );
        }
    }
}