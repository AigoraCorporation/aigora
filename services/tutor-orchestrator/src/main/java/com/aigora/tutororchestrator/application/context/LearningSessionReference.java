package com.aigora.tutororchestrator.application.context;

import com.aigora.tutororchestrator.domain.valueobjects.LearningSessionId;
import com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId;

public record LearningSessionReference(
        LearningSessionId learningSessionId,
        ExerciseAttemptId exerciseAttemptId
) {
}