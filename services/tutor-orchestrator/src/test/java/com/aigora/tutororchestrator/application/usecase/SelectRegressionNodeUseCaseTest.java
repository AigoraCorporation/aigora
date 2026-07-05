package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.policy.RegressionPolicy;
import com.aigora.tutororchestrator.domain.ranking.DeterministicCandidateRanking;
import com.aigora.tutororchestrator.domain.selection.DefaultSelectionStrategy;
import com.aigora.tutororchestrator.testsupport.fake.assessment.FakeAssessmentClient;
import com.aigora.tutororchestrator.testsupport.fake.curriculumgraph.FakeCurriculumGraphClient;
import com.aigora.tutororchestrator.testsupport.fake.studentmodel.FakeStudentModelClient;
import org.junit.jupiter.api.Test;

import java.util.List;

import static com.aigora.tutororchestrator.testsupport.assertion.DecisionAssertions.assertNoCandidateAvailable;
import static com.aigora.tutororchestrator.testsupport.assertion.DecisionAssertions.assertSelectedNode;
import static com.aigora.tutororchestrator.testsupport.builder.CommandBuilder.aCommand;
import static com.aigora.tutororchestrator.testsupport.fixture.Nodes.REGRESSION_NODE;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class SelectRegressionNodeUseCaseTest {

    @Test
    void shouldSelectRegressionNodeWhenRegressionIsRecommended() {
        var useCase = createUseCase(
                true,
                false,
                List.of(REGRESSION_NODE)
        );

        var result = useCase.execute(aCommand().buildSelectRegressionNodeCommand());

        assertSelectedNode(result.decision(), "node-prerequisite-001");
        assertEquals(DecisionStatus.SELECTED, result.decision().status());
        assertEquals("CANDIDATE_SELECTED", result.decision().reason().code());
    }

    @Test
    void shouldSelectRegressionNodeWhenCurrentNodeFailed() {
        var useCase = createUseCase(
                false,
                true,
                List.of(REGRESSION_NODE)
        );

        var result = useCase.execute(aCommand().buildSelectRegressionNodeCommand());

        assertSelectedNode(result.decision(), "node-prerequisite-001");
    }

    @Test
    void shouldReturnNoCandidateAvailableWhenRegressionIsNotRequired() {
        var useCase = createUseCase(
                false,
                false,
                List.of(REGRESSION_NODE)
        );

        var result = useCase.execute(aCommand().buildSelectRegressionNodeCommand());

        assertNoCandidateAvailable(result.decision());
    }

    @Test
    void shouldReturnNoCandidateAvailableWhenNoRegressionCandidatesAreAvailable() {
        var useCase = createUseCase(
                true,
                false,
                List.of()
        );

        var result = useCase.execute(aCommand().buildSelectRegressionNodeCommand());

        assertNoCandidateAvailable(result.decision());
    }

    @Test
    void shouldBeDeterministicForSameInputExceptGeneratedDecisionId() {
        var useCase = createUseCase(
                true,
                false,
                List.of(REGRESSION_NODE)
        );

        var first = useCase.execute(aCommand().buildSelectRegressionNodeCommand()).decision();
        var second = useCase.execute(aCommand().buildSelectRegressionNodeCommand()).decision();

        assertEquals(first.status(), second.status());
        assertEquals(first.studentId(), second.studentId());
        assertEquals(first.selectedNodeId(), second.selectedNodeId());
        assertEquals(first.reason(), second.reason());
        assertEquals(first.graphVersion(), second.graphVersion());
        assertEquals(first.correlationId(), second.correlationId());
    }

    @Test
    void shouldRejectNullCommand() {
        var useCase = createUseCase(
                true,
                false,
                List.of(REGRESSION_NODE)
        );

        assertThrows(IllegalArgumentException.class, () -> useCase.execute(null));
    }

    private SelectRegressionNodeUseCase createUseCase(
            boolean regressionRecommended,
            boolean failedCurrentNode,
            List<com.aigora.tutororchestrator.domain.valueobjects.NodeId> prerequisites
    ) {
        return new SelectRegressionNodeUseCase(
                new FakeCurriculumGraphClient(List.of(), prerequisites),
                new FakeStudentModelClient(regressionRecommended),
                new FakeAssessmentClient(false, failedCurrentNode),
                new RegressionPolicy(),
                new DeterministicCandidateRanking(),
                new DefaultSelectionStrategy()
        );
    }
}