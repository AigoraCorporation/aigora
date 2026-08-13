package com.aigora.tutororchestrator.application.context;

import com.aigora.tutororchestrator.domain.model.DecisionTrace;
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

import java.time.Clock;
import java.time.Instant;
import java.time.ZoneOffset;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class DecisionTraceFactoryTest {

    private static final Instant FIXED_INSTANT =
            Instant.parse("2026-08-12T20:00:00Z");

    private static final Clock FIXED_CLOCK =
            Clock.fixed(
                    FIXED_INSTANT,
                    ZoneOffset.UTC
            );

    @Test
    void shouldCreateDecisionTraceFromOrchestrationContext() {
        DecisionTraceFactory factory =
                new DecisionTraceFactory(FIXED_CLOCK);

        OrchestrationContext context =
                validOrchestrationContext();

        DecisionTrace trace =
                factory.create(context);

        assertEquals(
                context.requestId(),
                trace.orchestrationRequestId()
        );

        assertEquals(
                context.sessionReference().learningSessionId(),
                trace.learningSessionId()
        );

        assertEquals(
                context.sessionReference().exerciseAttemptId(),
                trace.exerciseAttemptId()
        );

        assertEquals(
                context.decisionEvidence().assessmentResultId(),
                trace.assessmentResultId()
        );

        assertEquals(
                context.decisionEvidence().studentModelVersion(),
                trace.studentModelVersion()
        );

        assertEquals(
                context.decisionEvidence().graphVersion(),
                trace.graphVersion()
        );

        assertEquals(
                context.decisionEvidence().policySetVersion(),
                trace.policySetVersion()
        );

        assertEquals(
                context.traceContext().correlationId(),
                trace.correlationId()
        );

        assertEquals(
                context.traceContext().causationId(),
                trace.causationId()
        );

        assertEquals(
                FIXED_INSTANT,
                trace.decidedAt()
        );
    }

    @Test
    void shouldUseInjectedClockForDecisionTimestamp() {
        DecisionTraceFactory factory =
                new DecisionTraceFactory(FIXED_CLOCK);

        DecisionTrace trace =
                factory.create(
                        validOrchestrationContext()
                );

        assertEquals(
                FIXED_INSTANT,
                trace.decidedAt()
        );
    }

    @Test
    void shouldBeDeterministicForSameContextAndClock() {
        DecisionTraceFactory factory =
                new DecisionTraceFactory(FIXED_CLOCK);

        OrchestrationContext context =
                validOrchestrationContext();

        DecisionTrace first =
                factory.create(context);

        DecisionTrace second =
                factory.create(context);

        assertEquals(first, second);
    }

    @Test
    void shouldRejectNullClock() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new DecisionTraceFactory(null)
        );
    }

    @Test
    void shouldRejectNullOrchestrationContext() {
        DecisionTraceFactory factory =
                new DecisionTraceFactory(FIXED_CLOCK);

        assertThrows(
                IllegalArgumentException.class,
                () -> factory.create(null)
        );
    }

    private OrchestrationContext validOrchestrationContext() {
        return new OrchestrationContext(
                new OrchestrationRequestId("request-001"),
                new StudentId("student-001"),
                new LearningSessionReference(
                        new LearningSessionId("session-001"),
                        new ExerciseAttemptId("attempt-001")
                ),
                new DecisionEvidenceContext(
                        new AssessmentResultId("assessment-001"),
                        new StudentModelVersion("student-model-v3"),
                        new GraphVersion("graph-v2"),
                        new PolicySetVersion("policy-set-v1")
                ),
                new TraceContext(
                        new CorrelationId("correlation-001"),
                        new CausationId("exercise-completed-001")
                )
        );
    }
}