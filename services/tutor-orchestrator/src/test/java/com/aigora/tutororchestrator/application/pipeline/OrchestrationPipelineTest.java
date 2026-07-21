package com.aigora.tutororchestrator.application.pipeline;

import com.aigora.tutororchestrator.application.contracts.result.OrchestrationRoute;
import com.aigora.tutororchestrator.application.engine.DecisionEngine;
import com.aigora.tutororchestrator.application.usecase.EvaluateLearningProgressUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectNextLearningNodeUseCase;
import com.aigora.tutororchestrator.application.usecase.SelectRegressionNodeUseCase;
import com.aigora.tutororchestrator.domain.model.CandidateClassification;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.policy.CompletionPolicy;
import com.aigora.tutororchestrator.domain.policy.EligibilityPolicy;
import com.aigora.tutororchestrator.domain.policy.RegressionPolicy;
import com.aigora.tutororchestrator.domain.ranking.DeterministicCandidateRanking;
import com.aigora.tutororchestrator.domain.selection.DefaultSelectionStrategy;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.testsupport.fake.assessment.FakeAssessmentClient;
import com.aigora.tutororchestrator.testsupport.fake.curriculumgraph.FakeCurriculumGraphClient;
import com.aigora.tutororchestrator.testsupport.fake.studentmodel.FakeStudentModelClient;
import org.junit.jupiter.api.Test;

import java.util.List;

import static com.aigora.tutororchestrator.testsupport.assertion.DecisionAssertions.assertSelectedNode;
import static com.aigora.tutororchestrator.testsupport.builder.CommandBuilder.aCommand;
import static org.junit.jupiter.api.Assertions.*;

class OrchestrationPipelineTest {

    @Test
    void shouldRouteToNextLearningNodeWhenCurrentNodeIsCompleted() {
        var pipeline = createPipeline(
                true,
                false,
                false,
                List.of(
                        candidate(
                                "node-003",
                                CandidateClassification.REVIEW
                        ),
                        candidate(
                                "node-002",
                                CandidateClassification.NEXT_LEARNING
                        )
                ),
                List.of()
        );

        var result = pipeline.execute(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        assertEquals(
                OrchestrationRoute.NEXT_LEARNING_NODE,
                result.route()
        );
        assertTrue(result.progress().completed());
        assertFalse(result.progress().regressionRecommended());
        assertTrue(result.decision().isPresent());

        assertSelectedNode(
                result.decision().orElseThrow(),
                "node-002"
        );
    }

    @Test
    void shouldRouteToRegressionNodeWhenCurrentNodeFailed() {
        var pipeline = createPipeline(
                false,
                true,
                false,
                List.of(),
                List.of(
                        new NodeId("node-prerequisite-002"),
                        new NodeId("node-prerequisite-001")
                )
        );

        var result = pipeline.execute(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        assertEquals(
                OrchestrationRoute.REGRESSION_NODE,
                result.route()
        );
        assertFalse(result.progress().completed());
        assertTrue(result.progress().regressionRecommended());
        assertTrue(result.decision().isPresent());

        assertSelectedNode(
                result.decision().orElseThrow(),
                "node-prerequisite-001"
        );
    }

    @Test
    void shouldRouteToRegressionNodeWhenStudentModelRecommendsRegression() {
        var pipeline = createPipeline(
                false,
                false,
                true,
                List.of(),
                List.of(new NodeId("node-prerequisite-001"))
        );

        var result = pipeline.execute(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        assertEquals(
                OrchestrationRoute.REGRESSION_NODE,
                result.route()
        );
        assertTrue(result.progress().regressionRecommended());

        assertSelectedNode(
                result.decision().orElseThrow(),
                "node-prerequisite-001"
        );
    }

    @Test
    void shouldReturnLearningInProgressWithoutSelectingNode() {
        var pipeline = createPipeline(
                false,
                false,
                false,
                List.of(
                        candidate(
                                "node-002",
                                CandidateClassification.NEXT_LEARNING
                        )
                ),
                List.of(new NodeId("node-prerequisite-001"))
        );

        var result = pipeline.execute(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        assertEquals(
                OrchestrationRoute.LEARNING_IN_PROGRESS,
                result.route()
        );
        assertFalse(result.progress().completed());
        assertFalse(result.progress().regressionRecommended());
        assertTrue(result.decision().isEmpty());
        assertEquals(
                "LEARNING_IN_PROGRESS",
                result.progress().reason().code()
        );
    }

    @Test
    void shouldReturnNoCandidateDecisionWhenProgressCompletedButNoNextCandidateExists() {
        var pipeline = createPipeline(
                true,
                false,
                false,
                List.of(),
                List.of()
        );

        var result = pipeline.execute(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        assertEquals(
                OrchestrationRoute.NEXT_LEARNING_NODE,
                result.route()
        );

        var decision = result.decision().orElseThrow();

        assertNull(decision.selectedNodeId());
        assertEquals(
                "NO_CANDIDATE_AVAILABLE",
                decision.reason().code()
        );
    }

    @Test
    void shouldReturnNoCandidateDecisionWhenRegressionCandidateDoesNotExist() {
        var pipeline = createPipeline(
                false,
                true,
                false,
                List.of(),
                List.of()
        );

        var result = pipeline.execute(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        assertEquals(
                OrchestrationRoute.REGRESSION_NODE,
                result.route()
        );

        var decision = result.decision().orElseThrow();

        assertNull(decision.selectedNodeId());
        assertEquals(
                "NO_CANDIDATE_AVAILABLE",
                decision.reason().code()
        );
    }

    @Test
    void shouldPrioritizeRegressionWhenNodeIsCompletedButRegressionIsRecommended() {
        var pipeline = createPipeline(
                true,
                false,
                true,
                List.of(
                        candidate(
                                "node-002",
                                CandidateClassification.NEXT_LEARNING
                        )
                ),
                List.of(new NodeId("node-prerequisite-001"))
        );

        var result = pipeline.execute(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        assertTrue(result.progress().completed());
        assertTrue(result.progress().regressionRecommended());
        assertEquals(
                OrchestrationRoute.REGRESSION_NODE,
                result.route()
        );

        assertSelectedNode(
                result.decision().orElseThrow(),
                "node-prerequisite-001"
        );
    }

    @Test
    void shouldBeDeterministicForSameInputExceptGeneratedDecisionId() {
        var pipeline = createPipeline(
                true,
                false,
                false,
                List.of(
                        candidate(
                                "node-003",
                                CandidateClassification.REVIEW
                        ),
                        candidate(
                                "node-002",
                                CandidateClassification.NEXT_LEARNING
                        )
                ),
                List.of()
        );

        var first = pipeline.execute(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        var second = pipeline.execute(
                aCommand().buildEvaluateLearningProgressCommand()
        );

        assertEquals(first.progress(), second.progress());
        assertEquals(first.route(), second.route());

        var firstDecision = first.decision().orElseThrow();
        var secondDecision = second.decision().orElseThrow();

        assertEquals(
                firstDecision.studentId(),
                secondDecision.studentId()
        );
        assertEquals(
                firstDecision.selectedNodeId(),
                secondDecision.selectedNodeId()
        );
        assertEquals(
                firstDecision.status(),
                secondDecision.status()
        );
        assertEquals(
                firstDecision.reason(),
                secondDecision.reason()
        );
        assertEquals(
                firstDecision.graphVersion(),
                secondDecision.graphVersion()
        );
        assertEquals(
                firstDecision.correlationId(),
                secondDecision.correlationId()
        );
    }

    @Test
    void shouldRejectNullCommand() {
        var pipeline = createDefaultPipeline();

        assertThrows(
                IllegalArgumentException.class,
                () -> pipeline.execute(null)
        );
    }

    @Test
    void shouldRejectNullDecisionEngine() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationPipeline(null)
        );
    }

    private OrchestrationPipeline createDefaultPipeline() {
        return createPipeline(
                false,
                false,
                false,
                List.of(),
                List.of()
        );
    }

    private OrchestrationPipeline createPipeline(
            boolean masteredCurrentNode,
            boolean failedCurrentNode,
            boolean regressionRecommended,
            List<LearningCandidate> nextCandidates,
            List<NodeId> prerequisites
    ) {
        var curriculumGraphClient = new FakeCurriculumGraphClient(
                nextCandidates,
                prerequisites
        );

        var studentModelClient = new FakeStudentModelClient(
                regressionRecommended
        );

        var assessmentClient = new FakeAssessmentClient(
                masteredCurrentNode,
                failedCurrentNode
        );

        var completionPolicy = new CompletionPolicy();
        var regressionPolicy = new RegressionPolicy();
        var candidateRanking = new DeterministicCandidateRanking();
        var selectionStrategy = new DefaultSelectionStrategy();

        var selectNextLearningNodeUseCase =
                new SelectNextLearningNodeUseCase(
                        curriculumGraphClient,
                        studentModelClient,
                        assessmentClient,
                        new EligibilityPolicy(),
                        completionPolicy,
                        regressionPolicy,
                        candidateRanking,
                        selectionStrategy
                );

        var selectRegressionNodeUseCase =
                new SelectRegressionNodeUseCase(
                        curriculumGraphClient,
                        studentModelClient,
                        assessmentClient,
                        regressionPolicy,
                        candidateRanking,
                        selectionStrategy
                );

        var evaluateLearningProgressUseCase =
                new EvaluateLearningProgressUseCase(
                        studentModelClient,
                        assessmentClient,
                        completionPolicy,
                        regressionPolicy
                );

        var decisionEngine = new DecisionEngine(
                selectNextLearningNodeUseCase,
                selectRegressionNodeUseCase,
                evaluateLearningProgressUseCase
        );

        return new OrchestrationPipeline(decisionEngine);
    }

    private LearningCandidate candidate(
            String nodeId,
            CandidateClassification classification
    ) {
        return new LearningCandidate(
                new NodeId(nodeId),
                classification
        );
    }
}