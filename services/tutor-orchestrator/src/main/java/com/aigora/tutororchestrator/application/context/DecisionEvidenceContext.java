package com.aigora.tutororchestrator.application.context;

import com.aigora.tutororchestrator.domain.valueobjects.*;

public record DecisionEvidenceContext(
        AssessmentResultId assessmentResultId,
        StudentModelVersion studentModelVersion,
        GraphVersion graphVersion,
        PolicySetVersion policySetVersion
) {
}