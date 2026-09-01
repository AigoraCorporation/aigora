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

import java.time.Instant;

/**
 * Immutable evidence describing the context used to produce an orchestration
 * decision.
 *
 * <p>The trace makes a pedagogical decision reproducible and auditable without
 * transferring ownership of Learning Session, Assessment, Student Model, or
 * Curriculum Graph state to the Tutor Orchestrator.</p>
 */
public record DecisionTrace(
        OrchestrationRequestId orchestrationRequestId,
        LearningSessionId learningSessionId,
        ExerciseAttemptId exerciseAttemptId,
        AssessmentResultId assessmentResultId,
        StudentModelVersion studentModelVersion,
        GraphVersion graphVersion,
        PolicySetVersion policySetVersion,
        CorrelationId correlationId,
        CausationId causationId,
        Instant decidedAt
) {

    public DecisionTrace {
        if (orchestrationRequestId == null) {
            throw new IllegalArgumentException(
                    "OrchestrationRequestId must not be null"
            );
        }

        if (learningSessionId == null) {
            throw new IllegalArgumentException(
                    "LearningSessionId must not be null"
            );
        }

        if (exerciseAttemptId == null) {
            throw new IllegalArgumentException(
                    "ExerciseAttemptId must not be null"
            );
        }

        if (assessmentResultId == null) {
            throw new IllegalArgumentException(
                    "AssessmentResultId must not be null"
            );
        }

        if (studentModelVersion == null) {
            throw new IllegalArgumentException(
                    "StudentModelVersion must not be null"
            );
        }

        if (graphVersion == null) {
            throw new IllegalArgumentException(
                    "GraphVersion must not be null"
            );
        }

        if (policySetVersion == null) {
            throw new IllegalArgumentException(
                    "PolicySetVersion must not be null"
            );
        }

        if (correlationId == null) {
            throw new IllegalArgumentException(
                    "CorrelationId must not be null"
            );
        }

        if (causationId == null) {
            throw new IllegalArgumentException(
                    "CausationId must not be null"
            );
        }

        if (decidedAt == null) {
            throw new IllegalArgumentException(
                    "DecidedAt must not be null"
            );
        }
    }
}