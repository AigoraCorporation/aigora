package com.aigora.tutororchestrator.application.engine;

import com.aigora.tutororchestrator.application.context.DecisionTraceFactory;
import com.aigora.tutororchestrator.application.usecase.EvaluateLearningProgressUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectNextLearningNodeUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectRegressionNodeUseCase;
import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.policy.CompletionPolicy;
import com.aigora.tutororchestrator.domain.policy.EligibilityPolicy;
import com.aigora.tutororchestrator.domain.policy.RegressionPolicy;
import com.aigora.tutororchestrator.domain.ranking.DeterministicCandidateRanking;
import com.aigora.tutororchestrator.domain.selection.DefaultSelectionStrategy;
import com.aigora.tutororchestrator.testsupport.fake.assessment.FakeAssessmentClient;
import com.aigora.tutororchestrator.testsupport.fake.curriculumgraph.FakeCurriculumGraphClient;
import com.aigora.tutororchestrator.testsupport.fake.studentmodel.FakeStudentModelClient;
import org.junit.jupiter.api.Test;

import java.util.List;

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;

import static com.aigora.tutororchestrator.testsupport.assertion.DecisionAssertions.assertSelectedNode;
import static com.aigora.tutororchestrator.testsupport.builder.CandidateBuilder.aCandidate;
import static com.aigora.tutororchestrator.testsupport.builder.CommandBuilder.aCommand;
import static com.aigora.tutororchestrator.testsupport.fixture.Nodes.REGRESSION_NODE;
import static org.junit.jupiter.api.Assertions.*;

class DecisionEngineTest {

    @Test
    void shouldDelegateNextLearningNodeSelection() {
        var engine = createDecisionEngine(
                true,
                false,
                false,
                List.of(
                        aCandidate()
                                .withNodeId("node-003")
                                .withClassification(CandidateClassification.REVIEW)
                                .build(),
                        aCandidate()
                                .withNodeId("node-002")
                                .withClassification(CandidateClassification.NEXT_LEARNING)
                                .build()
                ),
                List.of()
        );

        var result = engine.selectNextLearningNode(
                aCommand().buildSelectNextLearningNodeCommand()
        );

        assertSelectedNode(result.decision(), "node-002");
        assertEquals(DecisionStatus.SELECTED, result.decision().status());
    }

    @Test
    void shouldDelegateRegressionNodeSelection() {
        var engine = createDecisionEngine(
                false,
                true,
                false,
                List.of(),
                List.of(REGRESSION_NODE)
        );

        var result = engine.selectRegressionNode(
                aCommand().buildSelectRegressionNodeCommand()
        );

        assertSelectedNode(result.decision(), "node-prerequisite-001");
        assertEquals(DecisionStatus.SELECTED, result.decision().status());
    }

    @Test
    void shouldDelegateLearningProgressEvaluation() {
        var engine = createDecisionEngine(
                true,
                false,
                false,
                List.of(),
                List.of()
        );

        var result = engine.evaluateLearningProgress(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        assertTrue(result.completed());
        assertFalse(result.regressionRecommended());
        assertEquals("LEARNING_COMPLETED", result.reason().code());
    }

    @Test
    void shouldReturnRegressionRecommendationFromProgressEvaluation() {
        var engine = createDecisionEngine(
                false,
                true,
                false,
                List.of(),
                List.of()
        );

        var result = engine.evaluateLearningProgress(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        assertFalse(result.completed());
        assertTrue(result.regressionRecommended());
        assertEquals("REGRESSION_RECOMMENDED", result.reason().code());
    }

    @Test
    void shouldRejectNullNextLearningNodeCommand() {
        var engine = createDefaultDecisionEngine();

        assertThrows(
                IllegalArgumentException.class,
                () -> engine.selectNextLearningNode(null)
        );
    }

    @Test
    void shouldRejectNullRegressionNodeCommand() {
        var engine = createDefaultDecisionEngine();

        assertThrows(
                IllegalArgumentException.class,
                () -> engine.selectRegressionNode(null)
        );
    }

    @Test
    void shouldRejectNullEvaluateLearningProgressCommand() {
        var engine = createDefaultDecisionEngine();

        assertThrows(
                IllegalArgumentException.class,
                () -> engine.evaluateLearningProgress(null)
        );
    }

    @Test
    void shouldRejectNullSelectNextLearningNodeUseCase() {
        var dependencies = dependencies();

        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionEngine(
                        null,
                        dependencies.selectRegressionNodeUseCase(),
                        dependencies.evaluateLearningProgressUseCase()
                )
        );
    }

    @Test
    void shouldRejectNullSelectRegressionNodeUseCase() {
        var dependencies = dependencies();

        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionEngine(
                        dependencies.selectNextLearningNodeUseCase(),
                        null,
                        dependencies.evaluateLearningProgressUseCase()
                )
        );
    }

    @Test
    void shouldRejectNullEvaluateLearningProgressUseCase() {
        var dependencies = dependencies();

        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionEngine(
                        dependencies.selectNextLearningNodeUseCase(),
                        dependencies.selectRegressionNodeUseCase(),
                        null
                )
        );
    }

    private DecisionEngine createDefaultDecisionEngine() {
        return createDecisionEngine(
                true,
                false,
                false,
                List.of(),
                List.of()
        );
    }

    private DecisionEngine createDecisionEngine(
            boolean masteredCurrentNode,
            boolean failedCurrentNode,
            boolean regressionRecommended,
            List<com.aigora.tutororchestrator.domain.model.LearningCandidate> candidates,
            List<com.aigora.tutororchestrator.domain.valueobjects.NodeId> prerequisites
    ) {
        var curriculumGraphClient =
                new FakeCurriculumGraphClient(candidates, prerequisites);

        var studentModelClient =
                new FakeStudentModelClient(regressionRecommended);

        var assessmentClient =
                new FakeAssessmentClient(masteredCurrentNode, failedCurrentNode);

        var eligibilityPolicy = new EligibilityPolicy();
        var completionPolicy = new CompletionPolicy();
        var regressionPolicy = new RegressionPolicy();
        var candidateRanking = new DeterministicCandidateRanking();
        var selectionStrategy = new DefaultSelectionStrategy();

        var selectNextLearningNodeUseCase = new SelectNextLearningNodeUseCase(
                curriculumGraphClient,
                studentModelClient,
                assessmentClient,
                eligibilityPolicy,
                completionPolicy,
                regressionPolicy,
                candidateRanking,
                selectionStrategy,
                fixedDecisionTraceFactory()
        );

        var selectRegressionNodeUseCase = new SelectRegressionNodeUseCase(
                curriculumGraphClient,
                studentModelClient,
                assessmentClient,
                regressionPolicy,
                candidateRanking,
                selectionStrategy,
                fixedDecisionTraceFactory()
        );

        var evaluateLearningProgressUseCase = new EvaluateLearningProgressUseCase(
                studentModelClient,
                assessmentClient,
                completionPolicy,
                regressionPolicy
        );

        return new DecisionEngine(
                selectNextLearningNodeUseCase,
                selectRegressionNodeUseCase,
                evaluateLearningProgressUseCase
        );
    }

    private UseCaseDependencies dependencies() {
        var curriculumGraphClient =
                new FakeCurriculumGraphClient(List.of(), List.of());

        var studentModelClient =
                new FakeStudentModelClient(false);

        var assessmentClient =
                new FakeAssessmentClient(true, false);

        var completionPolicy = new CompletionPolicy();
        var regressionPolicy = new RegressionPolicy();
        var candidateRanking = new DeterministicCandidateRanking();
        var selectionStrategy = new DefaultSelectionStrategy();

        return new UseCaseDependencies(
                new SelectNextLearningNodeUseCase(
                        curriculumGraphClient,
                        studentModelClient,
                        assessmentClient,
                        new EligibilityPolicy(),
                        completionPolicy,
                        regressionPolicy,
                        candidateRanking,
                        selectionStrategy,
                        fixedDecisionTraceFactory()
                ),
                new SelectRegressionNodeUseCase(
                        curriculumGraphClient,
                        studentModelClient,
                        assessmentClient,
                        regressionPolicy,
                        candidateRanking,
                        selectionStrategy,
                        fixedDecisionTraceFactory()
                ),
                new EvaluateLearningProgressUseCase(
                        studentModelClient,
                        assessmentClient,
                        completionPolicy,
                        regressionPolicy
                )
        );
    }

    private record UseCaseDependencies(
            SelectNextLearningNodeUseCase selectNextLearningNodeUseCase,
            SelectRegressionNodeUseCase selectRegressionNodeUseCase,
            EvaluateLearningProgressUseCase evaluateLearningProgressUseCase
    ) {
    }

    private DecisionTraceFactory fixedDecisionTraceFactory() {
        return new DecisionTraceFactory(
                Clock.fixed(
                        Instant.parse("2026-08-15T20:00:00Z"),
                        ZoneOffset.UTC
                )
        );
    }
}