package com.aigora.tutororchestrator.domain.selection;

import com.aigora.tutororchestrator.domain.model.DecisionTrace;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

import java.util.List;

public interface SelectionStrategy {

    OrchestrationDecision select(
            List<LearningCandidate> rankedCandidates,
            StudentId studentId,
            DecisionTrace decisionTrace
    );
}