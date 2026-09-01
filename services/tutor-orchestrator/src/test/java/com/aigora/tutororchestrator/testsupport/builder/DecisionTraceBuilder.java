package com.aigora.tutororchestrator.testsupport.builder;

import com.aigora.tutororchestrator.domain.model.DecisionTrace;
import com.aigora.tutororchestrator.domain.valueobjects.*;

import java.time.Instant;

public final class DecisionTraceBuilder {

    private OrchestrationRequestId requestId = new OrchestrationRequestId("request-001");
    private LearningSessionId learningSessionId = new LearningSessionId("session-001");
    private ExerciseAttemptId exerciseAttemptId = new ExerciseAttemptId("attempt-001");
    private AssessmentResultId assessmentResultId = new AssessmentResultId("assessment-001");
    private StudentModelVersion studentModelVersion = new StudentModelVersion("student-model-v1");
    private GraphVersion graphVersion = new GraphVersion("v1.0.0");
    private PolicySetVersion policySetVersion = new PolicySetVersion("policy-set-v1");
    private CorrelationId correlationId = new CorrelationId("corr-001");
    private CausationId causationId = new CausationId("cause-001");
    private Instant decidedAt = Instant.parse("2026-08-15T20:00:00Z");

    private DecisionTraceBuilder() {}

    public static DecisionTraceBuilder aDecisionTrace() {
        return new DecisionTraceBuilder();
    }

    public DecisionTraceBuilder withGraphVersion(String value) {
        this.graphVersion = new GraphVersion(value);
        return this;
    }

    public DecisionTraceBuilder withCorrelationId(String value) {
        this.correlationId = new CorrelationId(value);
        return this;
    }

    public DecisionTrace build() {
        return new DecisionTrace(
                requestId, learningSessionId, exerciseAttemptId, assessmentResultId,
                studentModelVersion, graphVersion, policySetVersion, correlationId,
                causationId, decidedAt
        );
    }
}
