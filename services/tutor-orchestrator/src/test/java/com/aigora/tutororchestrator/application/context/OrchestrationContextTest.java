package com.aigora.tutororchestrator.application.context;

import com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId;
import com.aigora.tutororchestrator.domain.valueobjects.CausationId;
import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.LearningSessionId;
import com.aigora.tutororchestrator.domain.valueobjects.OrchestrationRequestId;
import com.aigora.tutororchestrator.domain.valueobjects.PolicySetVersion;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class OrchestrationContextTest {

    @Test
    void shouldCreateCompleteOrchestrationContext() {
        OrchestrationContext context = validContext();

        assertEquals(
                new OrchestrationRequestId("request-001"),
                context.requestId()
        );

        assertEquals(
                new StudentId("student-001"),
                context.studentId()
        );

        assertEquals(
                new LearningSessionId("session-001"),
                context.sessionReference().learningSessionId()
        );

        assertEquals(
                new ExerciseAttemptId("attempt-001"),
                context.sessionReference().exerciseAttemptId()
        );

        assertEquals(
                new AssessmentResultId("assessment-001"),
                context.decisionEvidence().assessmentResultId()
        );

        assertEquals(
                new StudentModelVersion("student-model-v10"),
                context.decisionEvidence().studentModelVersion()
        );

        assertEquals(
                new GraphVersion("graph-v4"),
                context.decisionEvidence().graphVersion()
        );

        assertEquals(
                new PolicySetVersion("policy-set-v2"),
                context.decisionEvidence().policySetVersion()
        );

        assertEquals(
                new CorrelationId("correlation-001"),
                context.traceContext().correlationId()
        );

        assertEquals(
                new CausationId("exercise-completed-001"),
                context.traceContext().causationId()
        );
    }

    @Test
    void shouldRejectNullRequestId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationContext(
                        null,
                        new StudentId("student-001"),
                        validSessionReference(),
                        validDecisionEvidence(),
                        validTraceContext()
                )
        );
    }

    @Test
    void shouldRejectNullStudentId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationContext(
                        new OrchestrationRequestId("request-001"),
                        null,
                        validSessionReference(),
                        validDecisionEvidence(),
                        validTraceContext()
                )
        );
    }

    @Test
    void shouldRejectNullSessionReference() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationContext(
                        new OrchestrationRequestId("request-001"),
                        new StudentId("student-001"),
                        null,
                        validDecisionEvidence(),
                        validTraceContext()
                )
        );
    }

    @Test
    void shouldRejectNullDecisionEvidence() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationContext(
                        new OrchestrationRequestId("request-001"),
                        new StudentId("student-001"),
                        validSessionReference(),
                        null,
                        validTraceContext()
                )
        );
    }

    @Test
    void shouldRejectNullTraceContext() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new OrchestrationContext(
                        new OrchestrationRequestId("request-001"),
                        new StudentId("student-001"),
                        validSessionReference(),
                        validDecisionEvidence(),
                        null
                )
        );
    }

    private OrchestrationContext validContext() {
        return new OrchestrationContext(
                new OrchestrationRequestId("request-001"),
                new StudentId("student-001"),
                validSessionReference(),
                validDecisionEvidence(),
                validTraceContext()
        );
    }

    private LearningSessionReference validSessionReference() {
        return new LearningSessionReference(
                new LearningSessionId("session-001"),
                new ExerciseAttemptId("attempt-001")
        );
    }

    private DecisionEvidenceContext validDecisionEvidence() {
        return new DecisionEvidenceContext(
                new AssessmentResultId("assessment-001"),
                new StudentModelVersion("student-model-v10"),
                new GraphVersion("graph-v4"),
                new PolicySetVersion("policy-set-v2")
        );
    }

    private TraceContext validTraceContext() {
        return new TraceContext(
                new CorrelationId("correlation-001"),
                new CausationId("exercise-completed-001")
        );
    }
}