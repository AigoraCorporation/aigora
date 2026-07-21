package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.application.contracts.command.SelectRegressionNodeCommand;
import com.aigora.tutororchestrator.application.contracts.result.SelectRegressionNodeResult;
import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import com.aigora.tutororchestrator.application.ports.CurriculumGraphClient;
import com.aigora.tutororchestrator.application.ports.StudentModelClient;
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
        if (curriculumGraphClient == null) throw new IllegalArgumentException("CurriculumGraphClient must not be null");
        if (studentModelClient == null) throw new IllegalArgumentException("StudentModelClient must not be null");
        if (assessmentClient == null) throw new IllegalArgumentException("AssessmentClient must not be null");
        if (regressionPolicy == null) throw new IllegalArgumentException("RegressionPolicy must not be null");
        if (candidateRanking == null) throw new IllegalArgumentException("DeterministicCandidateRanking must not be null");
        if (selectionStrategy == null) throw new IllegalArgumentException("SelectionStrategy must not be null");

        this.curriculumGraphClient = curriculumGraphClient;
        this.studentModelClient = studentModelClient;
        this.assessmentClient = assessmentClient;
        this.regressionPolicy = regressionPolicy;
        this.candidateRanking = candidateRanking;
        this.selectionStrategy = selectionStrategy;
    }

    public SelectRegressionNodeResult execute(SelectRegressionNodeCommand command) {
        if (command == null) {
            throw new IllegalArgumentException("SelectRegressionNodeCommand must not be null");
        }

        StudentLearningState studentLearningState =
                studentModelClient.getLearningState(command.studentId());

        boolean failedCurrentNode = assessmentClient.hasFailedNode(
                command.studentId(),
                command.currentNodeId()
        );

        boolean regressionRecommended =
                studentModelClient.isRegressionRecommended(command.studentId());

        boolean shouldRegress =
                regressionPolicy.shouldRegress(failedCurrentNode, regressionRecommended);

        if (!shouldRegress) {
            return new SelectRegressionNodeResult(
                    selectionStrategy.select(
                            List.of(),
                            command.studentId(),
                            command.graphVersion(),
                            command.correlationId()
                    )
            );
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
                        command.studentId(),
                        command.graphVersion(),
                        command.correlationId()
                )
        );
    }
}