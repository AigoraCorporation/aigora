package com.aigora.tutororchestrator.domain.model;

import com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId;
import com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;

import java.math.BigDecimal;

public record AssessmentSnapshot(
        AssessmentResultId assessmentResultId,
        ExerciseAttemptId exerciseAttemptId,
        NodeId nodeId,
        boolean mastered,
        boolean failed,
        BigDecimal score,
        BigDecimal confidence
) {

    public AssessmentSnapshot {
        if (assessmentResultId == null) {
            throw new IllegalArgumentException(
                    "AssessmentResultId must not be null"
            );
        }

        if (exerciseAttemptId == null) {
            throw new IllegalArgumentException(
                    "ExerciseAttemptId must not be null"
            );
        }

        if (nodeId == null) {
            throw new IllegalArgumentException(
                    "NodeId must not be null"
            );
        }

        if (score == null) {
            throw new IllegalArgumentException(
                    "Score must not be null"
            );
        }

        if (confidence == null) {
            throw new IllegalArgumentException(
                    "Confidence must not be null"
            );
        }

        if (score.compareTo(BigDecimal.ZERO) < 0
                || score.compareTo(BigDecimal.ONE) > 0) {
            throw new IllegalArgumentException(
                    "Score must be between 0 and 1"
            );
        }

        if (confidence.compareTo(BigDecimal.ZERO) < 0
                || confidence.compareTo(BigDecimal.ONE) > 0) {
            throw new IllegalArgumentException(
                    "Confidence must be between 0 and 1"
            );
        }

        if (mastered && failed) {
            throw new IllegalArgumentException(
                    "Assessment cannot be mastered and failed simultaneously"
            );
        }
    }
}