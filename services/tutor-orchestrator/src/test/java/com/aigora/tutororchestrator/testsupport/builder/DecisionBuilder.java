package com.aigora.tutororchestrator.testsupport.builder;

import com.aigora.tutororchestrator.domain.model.DecisionReason;
import com.aigora.tutororchestrator.domain.model.DecisionStatus;
import com.aigora.tutororchestrator.domain.model.DecisionTrace;
import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;
import com.aigora.tutororchestrator.domain.valueobjects.DecisionId;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

import static com.aigora.tutororchestrator.testsupport.builder.DecisionTraceBuilder.aDecisionTrace;

public final class DecisionBuilder {

    private DecisionId decisionId = new DecisionId("decision-001");
    private StudentId studentId = new StudentId("student-001");
    private NodeId selectedNodeId = new NodeId("node-002");
    private DecisionStatus status = DecisionStatus.SELECTED;
    private DecisionReason reason = new DecisionReason(
            "CANDIDATE_SELECTED",
            "The highest-ranked candidate was selected"
    );
    private DecisionTrace trace = aDecisionTrace().build();

    private DecisionBuilder() {}

    public static DecisionBuilder aDecision() {
        return new DecisionBuilder();
    }

    public DecisionBuilder withSelectedNodeId(String nodeId) {
        this.selectedNodeId = new NodeId(nodeId);
        return this;
    }

    public DecisionBuilder withTrace(DecisionTrace trace) {
        this.trace = trace;
        return this;
    }

    public DecisionBuilder asNoCandidateAvailable() {
        this.selectedNodeId = null;
        this.status = DecisionStatus.NO_CANDIDATE_AVAILABLE;
        this.reason = new DecisionReason(
                "NO_CANDIDATE_AVAILABLE",
                "No ranked candidates were available for selection"
        );
        return this;
    }

    public OrchestrationDecision build() {
        return new OrchestrationDecision(
                decisionId, studentId, selectedNodeId, status, reason, trace
        );
    }
}
