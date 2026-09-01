package com.aigora.tutororchestrator.application.ports;

import com.aigora.tutororchestrator.domain.model.AssessmentSnapshot;
import com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId;

public interface AssessmentClient {

    AssessmentSnapshot getAssessment(AssessmentResultId assessmentResultId);
}