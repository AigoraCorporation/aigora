package com.aigora.tutororchestrator.testsupport.fake.decisiontrace;

import com.aigora.tutororchestrator.application.ports.DecisionTraceSink;
import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;

import java.util.ArrayList;
import java.util.List;

/**
 * Test double for the decision trace recording boundary.
 *
 * <p>Stores orchestration decisions in memory so tests can verify
 * whether decision evidence was recorded correctly.</p>
 */
public final class FakeDecisionTraceSink implements DecisionTraceSink {

    private final List<OrchestrationDecision> recordedDecisions =
            new ArrayList<>();

    @Override
    public void record(OrchestrationDecision decision) {
        if (decision == null) {
            throw new IllegalArgumentException(
                    "OrchestrationDecision must not be null"
            );
        }

        recordedDecisions.add(decision);
    }

    /**
     * Returns an immutable snapshot of all recorded decisions.
     */
    public List<OrchestrationDecision> recordedDecisions() {
        return List.copyOf(recordedDecisions);
    }

    /**
     * Returns the most recently recorded decision.
     *
     * @throws IllegalStateException when no decision has been recorded
     */
    public OrchestrationDecision lastRecordedDecision() {
        if (recordedDecisions.isEmpty()) {
            throw new IllegalStateException(
                    "No orchestration decision has been recorded"
            );
        }

        return recordedDecisions.get(
                recordedDecisions.size() - 1
        );
    }

    /**
     * Returns the number of decisions recorded by this fake.
     */
    public int recordedDecisionCount() {
        return recordedDecisions.size();
    }
}