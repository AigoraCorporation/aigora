package com.aigora.tutororchestrator.application.context;
import com.aigora.tutororchestrator.domain.valueobjects.*; import com.aigora.tutororchestrator.shared.validation.Require;
public record SessionAssessmentSnapshot(AssessmentResultId assessmentResultId, ExerciseAttemptId attemptId, NodeId nodeId, boolean mastered, boolean failed) {
 public SessionAssessmentSnapshot { Require.nonNull(assessmentResultId,"AssessmentResultId");Require.nonNull(attemptId,"ExerciseAttemptId");Require.nonNull(nodeId,"NodeId");if(mastered&&failed)throw new IllegalArgumentException("Assessment cannot be mastered and failed simultaneously"); }
}
