package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.model.SessionDomainException;
import com.aigora.tutororchestrator.domain.valueobjects.*;
import com.aigora.tutororchestrator.shared.validation.Require;
import java.time.Instant;
public final class ExerciseAttempt {
    private final ExerciseAttemptId id;
    private final ExerciseId exerciseId;
    private final Instant completedAt;
    private ExerciseAttemptStatus status;
    private AssessmentResultId assessmentResultId;
    public ExerciseAttempt(ExerciseAttemptId id, ExerciseId exerciseId, Instant completedAt) {
        this.id=Require.nonNull(id,"ExerciseAttemptId"); this.exerciseId=Require.nonNull(exerciseId,"ExerciseId"); this.completedAt=Require.nonNull(completedAt,"completedAt"); this.status=ExerciseAttemptStatus.COMPLETED;
    }
    private ExerciseAttempt(ExerciseAttemptId id, ExerciseId exerciseId, Instant completedAt, ExerciseAttemptStatus status, AssessmentResultId assessmentResultId) {
        this.id=id; this.exerciseId=exerciseId; this.completedAt=completedAt; this.status=status; this.assessmentResultId=assessmentResultId;
    }
    public void acceptAssessment(AssessmentResultId resultId) {
        Require.nonNull(resultId,"AssessmentResultId");
        if (assessmentResultId != null) {
            if (assessmentResultId.equals(resultId)) return;
            throw new SessionDomainException("Assessment result cannot be replaced");
        }
        assessmentResultId=resultId; status=ExerciseAttemptStatus.ASSESSED;
    }
    public ExerciseAttempt copy() { return new ExerciseAttempt(id,exerciseId,completedAt,status,assessmentResultId); }
    public ExerciseAttemptId id(){return id;} public ExerciseId exerciseId(){return exerciseId;} public Instant completedAt(){return completedAt;} public ExerciseAttemptStatus status(){return status;} public AssessmentResultId assessmentResultId(){return assessmentResultId;}
}
