package com.aigora.tutororchestrator.testsupport.fake.decisiontrace;

import com.aigora.tutororchestrator.domain.model.DecisionReason;
import com.aigora.tutororchestrator.domain.model.DecisionReasonCode;
import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.model.DecisionTrace;
import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;
import com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId;
import com.aigora.tutororchestrator.domain.valueobjects.CausationId;
import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.DecisionId;
import com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.LearningSessionId;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.OrchestrationRequestId;
import com.aigora.tutororchestrator.domain.valueobjects.PolicySetVersion;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;
import org.junit.jupiter.api.Test;

import java.time.Instant;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class FakeDecisionTraceSinkTest {

    @Test
    void shouldRecordDecision() {
        FakeDecisionTraceSink sink =
                new FakeDecisionTraceSink();

        OrchestrationDecision decision =
                validDecision();

        sink.record(decision);

        assertEquals(
                1,
                sink.recordedDecisionCount()
        );

        assertEquals(
                decision,
                sink.lastRecordedDecision()
        );

        assertEquals(
                decision,
                sink.recordedDecisions().get(0)
        );
    }

    @Test
    void shouldRecordMultipleDecisionsInOrder() {
        FakeDecisionTraceSink sink =
                new FakeDecisionTraceSink();

        OrchestrationDecision first =
                validDecision();

        OrchestrationDecision second =
                anotherValidDecision();

        sink.record(first);
        sink.record(second);

        assertEquals(
                2,
                sink.recordedDecisionCount()
        );

        assertEquals(
                first,
                sink.recordedDecisions().get(0)
        );

        assertEquals(
                second,
                sink.recordedDecisions().get(1)
        );

        assertEquals(
                second,
                sink.lastRecordedDecision()
        );
    }

    @Test
    void shouldExposeRecordedDecisionsAsImmutableList() {
        FakeDecisionTraceSink sink =
                new FakeDecisionTraceSink();

        sink.record(validDecision());

        assertThrows(
                UnsupportedOperationException.class,
                () -> sink.recordedDecisions().clear()
        );
    }

    @Test
    void shouldRejectNullDecision() {
        FakeDecisionTraceSink sink =
                new FakeDecisionTraceSink();

        assertThrows(
                IllegalArgumentException.class,
                () -> sink.record(null)
        );
    }

    @Test
    void shouldFailWhenNoDecisionHasBeenRecorded() {
        FakeDecisionTraceSink sink =
                new FakeDecisionTraceSink();

        assertThrows(
                IllegalStateException.class,
                sink::lastRecordedDecision
        );
    }

    private OrchestrationDecision validDecision() {
        return new OrchestrationDecision(
                new DecisionId("decision-001"),
                new StudentId("student-001"),
                new NodeId("node-002"),
                DecisionStatus.SELECTED,
                new DecisionReason(
                        DecisionReasonCode.CANDIDATE_SELECTED,
                        "The highest-ranked candidate was selected"
                ),
                validDecisionTrace()
        );
    }

    private OrchestrationDecision anotherValidDecision() {
        return new OrchestrationDecision(
                new DecisionId("decision-002"),
                new StudentId("student-001"),
                null,
                DecisionStatus.NO_CANDIDATE_AVAILABLE,
                new DecisionReason(
                        DecisionReasonCode.NO_CANDIDATE_AVAILABLE,
                        "No ranked candidates were available for selection"
                ),
                validDecisionTrace()
        );
    }

    private DecisionTrace validDecisionTrace() {
        return new DecisionTrace(
                new OrchestrationRequestId("request-001"),
                new LearningSessionId("session-001"),
                new ExerciseAttemptId("attempt-001"),
                new AssessmentResultId("assessment-001"),
                new StudentModelVersion("student-model-v1"),
                new GraphVersion("graph-v1"),
                new PolicySetVersion("policy-set-v1"),
                new CorrelationId("correlation-001"),
                new CausationId("exercise-completed-001"),
                Instant.parse("2026-08-17T20:00:00Z")
        );
    }
}