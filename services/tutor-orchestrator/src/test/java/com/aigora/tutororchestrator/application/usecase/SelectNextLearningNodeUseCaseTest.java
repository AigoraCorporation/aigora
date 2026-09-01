package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.application.context.DecisionTraceFactory;
import com.aigora.tutororchestrator.domain.model.CandidateClassification;
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

import static com.aigora.tutororchestrator.testsupport.assertion.DecisionAssertions.assertNoCandidateAvailable;
import static com.aigora.tutororchestrator.testsupport.assertion.DecisionAssertions.assertSelectedNode;
import static com.aigora.tutororchestrator.testsupport.builder.CandidateBuilder.aCandidate;
import static com.aigora.tutororchestrator.testsupport.builder.CommandBuilder.aCommand;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class SelectNextLearningNodeUseCaseTest {

    @Test
    void shouldSelectNextLearningNodeWhenEligibleCandidatesAreAvailable() {
        var useCase = createUseCase(
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
                true,
                false,
                false
        );

        var result = useCase.execute(aCommand().buildSelectNextLearningNodeCommand());

        assertSelectedNode(result.decision(), "node-002");
        assertEquals("CANDIDATE_SELECTED", result.decision().reason().code());
    }

    @Test
    void shouldReturnNoCandidateAvailableWhenCandidateListIsEmpty() {
        var useCase = createUseCase(
                List.of(),
                true,
                false,
                false
        );

        var result = useCase.execute(aCommand().buildSelectNextLearningNodeCommand());

        assertNoCandidateAvailable(result.decision());
    }

    @Test
    void shouldReturnNoCandidateAvailableWhenCurrentNodeIsNotCompleted() {
        var useCase = createUseCase(
                List.of(
                        aCandidate()
                                .withNodeId("node-002")
                                .withClassification(CandidateClassification.NEXT_LEARNING)
                                .build()
                ),
                false,
                false,
                false
        );

        var result = useCase.execute(aCommand().buildSelectNextLearningNodeCommand());

        assertNoCandidateAvailable(result.decision());
    }

    @Test
    void shouldReturnNoCandidateAvailableWhenRegressionIsRecommended() {
        var useCase = createUseCase(
                List.of(
                        aCandidate()
                                .withNodeId("node-002")
                                .withClassification(CandidateClassification.NEXT_LEARNING)
                                .build()
                ),
                true,
                false,
                true
        );

        var result = useCase.execute(aCommand().buildSelectNextLearningNodeCommand());

        assertNoCandidateAvailable(result.decision());
    }

    @Test
    void shouldReturnNoCandidateAvailableWhenCurrentNodeFailed() {
       var useCase = createUseCase(
        List.of(
                aCandidate()
                        .withNodeId("node-002")
                        .withClassification(
                                CandidateClassification.NEXT_LEARNING
                        )
                        .build()
        ),
        false,
        true,
        false
        );

        var result = useCase.execute(aCommand().buildSelectNextLearningNodeCommand());

        assertNoCandidateAvailable(result.decision());
    }

    @Test
    void shouldFilterOutCurrentNodeCandidate() {
        var useCase = createUseCase(
                List.of(
                        aCandidate()
                                .withNodeId("node-001")
                                .withClassification(CandidateClassification.NEXT_LEARNING)
                                .build(),
                        aCandidate()
                                .withNodeId("node-002")
                                .withClassification(CandidateClassification.NEXT_LEARNING)
                                .build()
                ),
                true,
                false,
                false
        );

        var result = useCase.execute(aCommand().buildSelectNextLearningNodeCommand());

        assertSelectedNode(result.decision(), "node-002");
    }

    @Test
    void shouldFilterOutRegressionCandidatesForNextLearningNodeSelection() {
        var useCase = createUseCase(
                List.of(
                        aCandidate()
                                .withNodeId("node-prerequisite-001")
                                .withClassification(CandidateClassification.REGRESSION)
                                .build(),
                        aCandidate()
                                .withNodeId("node-003")
                                .withClassification(CandidateClassification.NEXT_LEARNING)
                                .build()
                ),
                true,
                false,
                false
        );

        var result = useCase.execute(aCommand().buildSelectNextLearningNodeCommand());

        assertSelectedNode(result.decision(), "node-003");
    }

    @Test
    void shouldBeDeterministicForSameInputExceptGeneratedDecisionId() {
        var useCase = createUseCase(
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
                true,
                false,
                false
        );

        var first = useCase.execute(aCommand().buildSelectNextLearningNodeCommand()).decision();
        var second = useCase.execute(aCommand().buildSelectNextLearningNodeCommand()).decision();

        assertEquals(first.status(), second.status());
        assertEquals(first.studentId(), second.studentId());
        assertEquals(first.selectedNodeId(), second.selectedNodeId());
        assertEquals(first.reason(), second.reason());
        assertEquals(first.trace().graphVersion(), second.trace().graphVersion());
        assertEquals(first.trace().correlationId(), second.trace().correlationId());
    }

    @Test
    void shouldRejectNullCommand() {
        var useCase = createUseCase(
                List.of(
                        aCandidate()
                                .withNodeId("node-002")
                                .withClassification(CandidateClassification.NEXT_LEARNING)
                                .build()
                ),
                true,
                false,
                false
        );

        assertThrows(IllegalArgumentException.class, () -> useCase.execute(null));
    }

    private SelectNextLearningNodeUseCase createUseCase(
            List<com.aigora.tutororchestrator.domain.model.LearningCandidate> candidates,
            boolean masteredCurrentNode,
            boolean failedCurrentNode,
            boolean regressionRecommended
    ) {
        return new SelectNextLearningNodeUseCase(
                new FakeCurriculumGraphClient(candidates),
                new FakeStudentModelClient(regressionRecommended),
                new FakeAssessmentClient(masteredCurrentNode, failedCurrentNode),
                new EligibilityPolicy(),
                new CompletionPolicy(),
                new RegressionPolicy(),
                new DeterministicCandidateRanking(),
                new DefaultSelectionStrategy(),
                fixedDecisionTraceFactory()
        );
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