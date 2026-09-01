package com.aigora.tutororchestrator.application.ports;
import com.aigora.tutororchestrator.application.context.SessionAssessmentSnapshot; import com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId;
public interface SessionAssessmentClient { SessionAssessmentSnapshot getAssessment(AssessmentResultId resultId); }
