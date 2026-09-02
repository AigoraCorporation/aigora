package com.aigora.tutororchestrator.application.usecase;

import com.aigora.tutororchestrator.domain.policy.CompletionPolicy;
import com.aigora.tutororchestrator.domain.policy.RegressionPolicy;
import com.aigora.tutororchestrator.testsupport.fake.assessment.FakeAssessmentClient;
import com.aigora.tutororchestrator.testsupport.fake.studentmodel.FakeStudentModelClient;
import org.junit.jupiter.api.Test;

import static com.aigora.tutororchestrator.testsupport.builder.CommandBuilder.aCommand;
import static com.aigora.tutororchestrator.testsupport.fixture.Students.STUDENT_001;
import static org.junit.jupiter.api.Assertions.*;

class EvaluateLearningProgressUseCaseTest {

    @Test
    void shouldEvaluateCompletedLearningProgress() {
        var useCase = createUseCase(
                true,
                false,
                false
        );

        var result = useCase.execute(aCommand().buildEvaluateLearningProgressCommand());

        assertEquals(STUDENT_001, result.studentId());
        assertTrue(result.completed());
        assertFalse(result.regressionRecommended());
        assertEquals("LEARNING_COMPLETED", result.reason().code());
    }

    @Test
    void shouldEvaluateLearningInProgressWhenCurrentNodeIsNotMastered() {
        var useCase = createUseCase(
                false,
                false,
                false
        );

        var result = useCase.execute(aCommand().buildEvaluateLearningProgressCommand());

        assertEquals(STUDENT_001, result.studentId());
        assertFalse(result.completed());
        assertFalse(result.regressionRecommended());
        assertEquals("LEARNING_IN_PROGRESS", result.reason().code());
    }

    @Test
    void shouldRecommendRegressionWhenCurrentNodeFailed() {
        var useCase = createUseCase(
                false,
                true,
                false
        );

        var result = useCase.execute(aCommand().buildEvaluateLearningProgressCommand());

        assertEquals(STUDENT_001, result.studentId());
        assertFalse(result.completed());
        assertTrue(result.regressionRecommended());
        assertEquals("REGRESSION_RECOMMENDED", result.reason().code());
    }

    @Test
    void shouldRecommendRegressionWhenStudentModelRecommendsRegression() {
        var useCase = createUseCase(
                false,
                false,
                true
        );

        var result = useCase.execute(aCommand().buildEvaluateLearningProgressCommand());

        assertEquals(STUDENT_001, result.studentId());
        assertFalse(result.completed());
        assertTrue(result.regressionRecommended());
        assertEquals("REGRESSION_RECOMMENDED", result.reason().code());
    }

    @Test
    void shouldPrioritizeRegressionReasonWhenCompletedAndRegressionRecommended() {
         var useCase = createUseCase(
            true,
            false,
            true
    );

        var result = useCase.execute(aCommand().buildEvaluateLearningProgressCommand());

        assertEquals(STUDENT_001, result.studentId());
        assertTrue(result.completed());
        assertTrue(result.regressionRecommended());
        assertEquals("REGRESSION_RECOMMENDED", result.reason().code());
    }

    @Test
    void shouldBeDeterministicForSameInput() {
        var useCase = createUseCase(
                true,
                false,
                false
        );

        var first = useCase.execute(aCommand().buildEvaluateLearningProgressCommand());
        var second = useCase.execute(aCommand().buildEvaluateLearningProgressCommand());

        assertEquals(first, second);
    }

    @Test
    void shouldRejectNullCommand() {
        var useCase = createUseCase(
                true,
                false,
                false
        );

        assertThrows(IllegalArgumentException.class, () -> useCase.execute(null));
    }

    private EvaluateLearningProgressUseCase createUseCase(
            boolean masteredCurrentNode,
            boolean failedCurrentNode,
            boolean regressionRecommended
    ) {
        return new EvaluateLearningProgressUseCase(
                new FakeStudentModelClient(regressionRecommended),
                new FakeAssessmentClient(masteredCurrentNode, failedCurrentNode),
                new CompletionPolicy(),
                new RegressionPolicy()
        );
    }
}