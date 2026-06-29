package com.aigora.tutororchestrator.domain.selection;

import com.aigora.tutororchestrator.domain.model.DecisionReason;
import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.model.LearningCandidate;
import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;
import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.DecisionId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

import java.util.List;

public final class DefaultSelectionStrategy implements SelectionStrategy {

    @Override
    public OrchestrationDecision select(
            List<LearningCandidate> rankedCandidates,
            StudentId studentId,
            GraphVersion graphVersion,
            CorrelationId correlationId
    ) {
        if (rankedCandidates == null) {
            throw new IllegalArgumentException("Ranked candidates must not be null");
        }

        if (studentId == null) {
            throw new IllegalArgumentException("StudentId must not be null");
        }

        if (graphVersion == null) {
            throw new IllegalArgumentException("GraphVersion must not be null");
        }

        if (correlationId == null) {
            throw new IllegalArgumentException("CorrelationId must not be null");
        }

        if (rankedCandidates.isEmpty()) {
            return noCandidateAvailableDecision(studentId, graphVersion, correlationId);
        }

        LearningCandidate selectedCandidate = rankedCandidates.get(0);

        return selectedDecision(
                selectedCandidate,
                studentId,
                graphVersion,
                correlationId
        );
    }

    private OrchestrationDecision selectedDecision(
            LearningCandidate candidate,
            StudentId studentId,
            GraphVersion graphVersion,
            CorrelationId correlationId
    ) {
        return new OrchestrationDecision(
                DecisionId.generate(),
                studentId,
                candidate.nodeId(),
                DecisionStatus.SELECTED,
                new DecisionReason(
                        "CANDIDATE_SELECTED",
                        "The highest-ranked candidate was selected"
                ),
                graphVersion,
                correlationId
        );
    }

    private OrchestrationDecision noCandidateAvailableDecision(
            StudentId studentId,
            GraphVersion graphVersion,
            CorrelationId correlationId
    ) {
        return new OrchestrationDecision(
                DecisionId.generate(),
                studentId,
                null,
                DecisionStatus.NO_CANDIDATE_AVAILABLE,
                new DecisionReason(
                        "NO_CANDIDATE_AVAILABLE",
                        "No ranked candidates were available for selection"
                ),
                graphVersion,
                correlationId
        );
    }
}