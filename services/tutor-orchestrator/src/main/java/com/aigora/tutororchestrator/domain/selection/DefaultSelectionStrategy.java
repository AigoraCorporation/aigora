package com.aigora.tutororchestrator.domain.selection;

import com.aigora.tutororchestrator.domain.model.DecisionReason;
import com.aigora.tutororchestrator.domain.model.DecisionReasonCode;
import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.model.DecisionTrace;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;
import com.aigora.tutororchestrator.domain.valueobjects.DecisionId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

import java.util.List;

import static com.aigora.tutororchestrator.shared.validation.Require.nonNull;
import static com.aigora.tutororchestrator.shared.validation.Require.withoutNullElements;

public final class DefaultSelectionStrategy implements SelectionStrategy {

    @Override
    public OrchestrationDecision select(
            List<LearningCandidate> rankedCandidates,
            StudentId studentId,
            DecisionTrace decisionTrace
    ) {
        withoutNullElements(
                rankedCandidates,
                "Ranked candidates"
        );

        nonNull(studentId, "StudentId");
        nonNull(decisionTrace, "DecisionTrace");

        if (rankedCandidates.isEmpty()) {
            return noCandidateAvailableDecision(
                    studentId,
                    decisionTrace
            );
        }

        LearningCandidate selectedCandidate =
                rankedCandidates.get(0);

        return selectedDecision(
                selectedCandidate,
                studentId,
                decisionTrace
        );
    }

    private OrchestrationDecision selectedDecision(
            LearningCandidate candidate,
            StudentId studentId,
            DecisionTrace decisionTrace
    ) {
        return new OrchestrationDecision(
                DecisionId.generate(),
                studentId,
                candidate.nodeId(),
                DecisionStatus.SELECTED,
                new DecisionReason(
                        DecisionReasonCode.CANDIDATE_SELECTED,
                        "The highest-ranked candidate was selected"
                ),
                decisionTrace
        );
    }

    private OrchestrationDecision noCandidateAvailableDecision(
            StudentId studentId,
            DecisionTrace decisionTrace
    ) {
        return new OrchestrationDecision(
                DecisionId.generate(),
                studentId,
                null,
                DecisionStatus.NO_CANDIDATE_AVAILABLE,
                new DecisionReason(
                        DecisionReasonCode.NO_CANDIDATE_AVAILABLE,
                        "No ranked candidates were available for selection"
                ),
                decisionTrace
        );
    }
}