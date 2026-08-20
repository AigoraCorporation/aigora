package com.aigora.tutororchestrator.application.configuration;

import com.aigora.tutororchestrator.application.context.DecisionTraceFactory;
import com.aigora.tutororchestrator.application.engine.DecisionEngine;
import com.aigora.tutororchestrator.application.pipeline.OrchestrationPipeline;
import com.aigora.tutororchestrator.application.ports.AssessmentClient;
import com.aigora.tutororchestrator.application.ports.CurriculumGraphClient;
import com.aigora.tutororchestrator.application.ports.DecisionTraceSink;
import com.aigora.tutororchestrator.application.ports.StudentModelClient;
import com.aigora.tutororchestrator.application.usecase.EvaluateLearningProgressUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectNextLearningNodeUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectRegressionNodeUseCase;
import com.aigora.tutororchestrator.domain.policy.CompletionPolicy;
import com.aigora.tutororchestrator.domain.policy.EligibilityPolicy;
import com.aigora.tutororchestrator.domain.policy.RegressionPolicy;
import com.aigora.tutororchestrator.domain.ranking.DeterministicCandidateRanking;
import com.aigora.tutororchestrator.domain.selection.DefaultSelectionStrategy;
import com.aigora.tutororchestrator.domain.selection.SelectionStrategy;

import java.time.Clock;

import static com.aigora.tutororchestrator.shared.validation.Require.nonNull;

/**
 * Framework-independent composition root for the Tutor Orchestrator.
 */
public final class DefaultTutorOrchestratorFactory {

    private final CurriculumGraphClient curriculumGraphClient;
    private final StudentModelClient studentModelClient;
    private final AssessmentClient assessmentClient;
    private final DecisionTraceSink decisionTraceSink;

    public DefaultTutorOrchestratorFactory(
            CurriculumGraphClient curriculumGraphClient,
            StudentModelClient studentModelClient,
            AssessmentClient assessmentClient,
            DecisionTraceSink decisionTraceSink
    ) {
        this.curriculumGraphClient = nonNull(
                curriculumGraphClient,
                "CurriculumGraphClient"
        );

        this.studentModelClient = nonNull(
                studentModelClient,
                "StudentModelClient"
        );

        this.assessmentClient = nonNull(
                assessmentClient,
                "AssessmentClient"
        );

        this.decisionTraceSink = nonNull(
                decisionTraceSink,
                "DecisionTraceSink"
        );
    }

    public TutorOrchestratorConfiguration build() {
        EligibilityPolicy eligibilityPolicy =
                new EligibilityPolicy();

        CompletionPolicy completionPolicy =
                new CompletionPolicy();

        RegressionPolicy regressionPolicy =
                new RegressionPolicy();

        DeterministicCandidateRanking candidateRanking =
                new DeterministicCandidateRanking();

        SelectionStrategy selectionStrategy =
                new DefaultSelectionStrategy();

        DecisionTraceFactory decisionTraceFactory =
                new DecisionTraceFactory(
                        Clock.systemUTC()
                );

        SelectNextLearningNodeUseCase selectNextLearningNodeUseCase =
                new SelectNextLearningNodeUseCase(
                        curriculumGraphClient,
                        studentModelClient,
                        assessmentClient,
                        eligibilityPolicy,
                        completionPolicy,
                        regressionPolicy,
                        candidateRanking,
                        selectionStrategy,
                        decisionTraceFactory
                );

        SelectRegressionNodeUseCase selectRegressionNodeUseCase =
                new SelectRegressionNodeUseCase(
                        curriculumGraphClient,
                        studentModelClient,
                        assessmentClient,
                        regressionPolicy,
                        candidateRanking,
                        selectionStrategy,
                        decisionTraceFactory
                );

        EvaluateLearningProgressUseCase evaluateLearningProgressUseCase =
                new EvaluateLearningProgressUseCase(
                        studentModelClient,
                        assessmentClient,
                        completionPolicy,
                        regressionPolicy
                );

        DecisionEngine decisionEngine =
                new DecisionEngine(
                        selectNextLearningNodeUseCase,
                        selectRegressionNodeUseCase,
                        evaluateLearningProgressUseCase
                );

        OrchestrationPipeline orchestrationPipeline =
                new OrchestrationPipeline(
                        decisionEngine,
                        decisionTraceSink
                );

        return new TutorOrchestratorConfiguration(
                selectNextLearningNodeUseCase,
                selectRegressionNodeUseCase,
                evaluateLearningProgressUseCase,
                decisionEngine,
                orchestrationPipeline
        );
    }
}