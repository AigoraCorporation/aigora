package com.aigora.tutororchestrator.application.contracts.result;

import com.aigora.tutororchestrator.domain.model.DecisionReason;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

public record EvaluateLearningProgressResult(
        StudentId studentId,
        boolean completed,
        boolean regressionRecommended,
        DecisionReason reason
) {
    public EvaluateLearningProgressResult {
        if (studentId == null) throw new IllegalArgumentException("StudentId must not be null");
        if (reason == null) throw new IllegalArgumentException("DecisionReason must not be null");
    }
}