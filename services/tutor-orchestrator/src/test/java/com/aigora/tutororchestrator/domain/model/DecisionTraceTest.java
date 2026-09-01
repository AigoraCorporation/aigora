package com.aigora.tutororchestrator.domain.model;

import com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId;
import com.aigora.tutororchestrator.domain.valueobjects.CausationId;
import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.LearningSessionId;
import com.aigora.tutororchestrator.domain.valueobjects.OrchestrationRequestId;
import com.aigora.tutororchestrator.domain.valueobjects.PolicySetVersion;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;
import org.junit.jupiter.api.Test;

import java.time.Instant;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class DecisionTraceTest {

    private static final OrchestrationRequestId REQUEST_ID =
            new OrchestrationRequestId("request-001");

    private static final LearningSessionId SESSION_ID =
            new LearningSessionId("session-001");

    private static final ExerciseAttemptId ATTEMPT_ID =
            new ExerciseAttemptId("attempt-001");

    private static final AssessmentResultId ASSESSMENT_RESULT_ID =
            new AssessmentResultId("assessment-001");

    private static final StudentModelVersion STUDENT_MODEL_VERSION =
            new StudentModelVersion("student-model-v3");

    private static final GraphVersion GRAPH_VERSION =
            new GraphVersion("graph-v2");

    private static final PolicySetVersion POLICY_SET_VERSION =
            new PolicySetVersion("policy-set-v1");

    private static final CorrelationId CORRELATION_ID =
            new CorrelationId("correlation-001");

    private static final CausationId CAUSATION_ID =
            new CausationId("exercise-completed-001");

    private static final Instant DECIDED_AT =
            Instant.parse("2026-08-11T20:00:00Z");

    @Test
    void shouldCreateDecisionTrace() {
        DecisionTrace trace = validDecisionTrace();

        assertEquals(
                REQUEST_ID,
                trace.orchestrationRequestId()
        );

        assertEquals(
                SESSION_ID,
                trace.learningSessionId()
        );

        assertEquals(
                ATTEMPT_ID,
                trace.exerciseAttemptId()
        );

        assertEquals(
                ASSESSMENT_RESULT_ID,
                trace.assessmentResultId()
        );

        assertEquals(
                STUDENT_MODEL_VERSION,
                trace.studentModelVersion()
        );

        assertEquals(
                GRAPH_VERSION,
                trace.graphVersion()
        );

        assertEquals(
                POLICY_SET_VERSION,
                trace.policySetVersion()
        );

        assertEquals(
                CORRELATION_ID,
                trace.correlationId()
        );

        assertEquals(
                CAUSATION_ID,
                trace.causationId()
        );

        assertEquals(
                DECIDED_AT,
                trace.decidedAt()
        );
    }

    @Test
    void shouldBeEqualWhenAllValuesAreEqual() {
        DecisionTrace first = validDecisionTrace();
        DecisionTrace second = validDecisionTrace();

        assertEquals(first, second);
    }

    @Test
    void shouldRejectNullOrchestrationRequestId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTrace(
                        null,
                        SESSION_ID,
                        ATTEMPT_ID,
                        ASSESSMENT_RESULT_ID,
                        STUDENT_MODEL_VERSION,
                        GRAPH_VERSION,
                        POLICY_SET_VERSION,
                        CORRELATION_ID,
                        CAUSATION_ID,
                        DECIDED_AT
                )
        );
    }

    @Test
    void shouldRejectNullLearningSessionId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTrace(
                        REQUEST_ID,
                        null,
                        ATTEMPT_ID,
                        ASSESSMENT_RESULT_ID,
                        STUDENT_MODEL_VERSION,
                        GRAPH_VERSION,
                        POLICY_SET_VERSION,
                        CORRELATION_ID,
                        CAUSATION_ID,
                        DECIDED_AT
                )
        );
    }

    @Test
    void shouldRejectNullExerciseAttemptId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTrace(
                        REQUEST_ID,
                        SESSION_ID,
                        null,
                        ASSESSMENT_RESULT_ID,
                        STUDENT_MODEL_VERSION,
                        GRAPH_VERSION,
                        POLICY_SET_VERSION,
                        CORRELATION_ID,
                        CAUSATION_ID,
                        DECIDED_AT
                )
        );
    }

    @Test
    void shouldRejectNullAssessmentResultId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTrace(
                        REQUEST_ID,
                        SESSION_ID,
                        ATTEMPT_ID,
                        null,
                        STUDENT_MODEL_VERSION,
                        GRAPH_VERSION,
                        POLICY_SET_VERSION,
                        CORRELATION_ID,
                        CAUSATION_ID,
                        DECIDED_AT
                )
        );
    }

    @Test
    void shouldRejectNullStudentModelVersion() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTrace(
                        REQUEST_ID,
                        SESSION_ID,
                        ATTEMPT_ID,
                        ASSESSMENT_RESULT_ID,
                        null,
                        GRAPH_VERSION,
                        POLICY_SET_VERSION,
                        CORRELATION_ID,
                        CAUSATION_ID,
                        DECIDED_AT
                )
        );
    }

    @Test
    void shouldRejectNullGraphVersion() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTrace(
                        REQUEST_ID,
                        SESSION_ID,
                        ATTEMPT_ID,
                        ASSESSMENT_RESULT_ID,
                        STUDENT_MODEL_VERSION,
                        null,
                        POLICY_SET_VERSION,
                        CORRELATION_ID,
                        CAUSATION_ID,
                        DECIDED_AT
                )
        );
    }

    @Test
    void shouldRejectNullPolicySetVersion() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTrace(
                        REQUEST_ID,
                        SESSION_ID,
                        ATTEMPT_ID,
                        ASSESSMENT_RESULT_ID,
                        STUDENT_MODEL_VERSION,
                        GRAPH_VERSION,
                        null,
                        CORRELATION_ID,
                        CAUSATION_ID,
                        DECIDED_AT
                )
        );
    }

    @Test
    void shouldRejectNullCorrelationId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTrace(
                        REQUEST_ID,
                        SESSION_ID,
                        ATTEMPT_ID,
                        ASSESSMENT_RESULT_ID,
                        STUDENT_MODEL_VERSION,
                        GRAPH_VERSION,
                        POLICY_SET_VERSION,
                        null,
                        CAUSATION_ID,
                        DECIDED_AT
                )
        );
    }

    @Test
    void shouldRejectNullCausationId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTrace(
                        REQUEST_ID,
                        SESSION_ID,
                        ATTEMPT_ID,
                        ASSESSMENT_RESULT_ID,
                        STUDENT_MODEL_VERSION,
                        GRAPH_VERSION,
                        POLICY_SET_VERSION,
                        CORRELATION_ID,
                        null,
                        DECIDED_AT
                )
        );
    }

    @Test
    void shouldRejectNullDecidedAt() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTrace(
                        REQUEST_ID,
                        SESSION_ID,
                        ATTEMPT_ID,
                        ASSESSMENT_RESULT_ID,
                        STUDENT_MODEL_VERSION,
                        GRAPH_VERSION,
                        POLICY_SET_VERSION,
                        CORRELATION_ID,
                        CAUSATION_ID,
                        null
                )
        );
    }

    private DecisionTrace validDecisionTrace() {
        return new DecisionTrace(
                REQUEST_ID,
                SESSION_ID,
                ATTEMPT_ID,
                ASSESSMENT_RESULT_ID,
                STUDENT_MODEL_VERSION,
                GRAPH_VERSION,
                POLICY_SET_VERSION,
                CORRELATION_ID,
                CAUSATION_ID,
                DECIDED_AT
        );
    }
}