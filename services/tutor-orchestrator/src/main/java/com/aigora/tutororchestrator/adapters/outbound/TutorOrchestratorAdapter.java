package com.aigora.tutororchestrator.adapters.outbound;

import com.aigora.tutororchestrator.application.context.SessionOrchestrationDecision;
import com.aigora.tutororchestrator.domain.model.OrchestrationOutcome;
import com.aigora.tutororchestrator.application.context.SessionOrchestrationRequest;
import com.aigora.tutororchestrator.application.ports.TutorOrchestratorClient;
import com.aigora.tutororchestrator.domain.valueobjects.DecisionId;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.application.context.DecisionEvidenceContext;
import com.aigora.tutororchestrator.application.context.LearningSessionReference;
import com.aigora.tutororchestrator.application.context.OrchestrationContext;
import com.aigora.tutororchestrator.application.context.TraceContext;
import com.aigora.tutororchestrator.application.contracts.command.EvaluateLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.result.OrchestrationRoute;
import com.aigora.tutororchestrator.application.pipeline.OrchestrationPipeline;
import com.aigora.tutororchestrator.domain.model.DecisionStatus;

import static com.aigora.tutororchestrator.shared.validation.Require.nonNull;

/** In-process adapter from Learning Session Engine to the deterministic Tutor Orchestrator. */
public final class TutorOrchestratorAdapter implements TutorOrchestratorClient {
    private final OrchestrationPipeline pipeline;

    public TutorOrchestratorAdapter(OrchestrationPipeline pipeline) {
        this.pipeline = nonNull(pipeline, "OrchestrationPipeline");
    }

    @Override
    public SessionOrchestrationDecision decide(SessionOrchestrationRequest request) {
        nonNull(request, "SessionOrchestrationRequest");

        var context = new OrchestrationContext(
                new com.aigora.tutororchestrator.domain.valueobjects.OrchestrationRequestId(request.requestId().value()),
                new com.aigora.tutororchestrator.domain.valueobjects.StudentId(request.studentId().value()),
                new LearningSessionReference(
                        new com.aigora.tutororchestrator.domain.valueobjects.LearningSessionId(request.sessionId().value()),
                        new com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId(request.attemptId().value())
                ),
                new DecisionEvidenceContext(
                        new com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId(request.assessmentResultId().value()),
                        new com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion(request.studentModelVersion().value()),
                        new com.aigora.tutororchestrator.domain.valueobjects.GraphVersion(request.graphVersion().value()),
                        new com.aigora.tutororchestrator.domain.valueobjects.PolicySetVersion(request.policySetVersion().value())
                ),
                new TraceContext(
                        new com.aigora.tutororchestrator.domain.valueobjects.CorrelationId(request.correlationId().value()),
                        new com.aigora.tutororchestrator.domain.valueobjects.CausationId(request.causationId().value())
                )
        );

        var result = pipeline.execute(
                new EvaluateLearningProgressCommand(
                        context,
                        new com.aigora.tutororchestrator.domain.valueobjects.NodeId(request.currentNodeId().value())
                )
        );

        if (result.route() == OrchestrationRoute.LEARNING_IN_PROGRESS) {
            return new SessionOrchestrationDecision(
                    new DecisionId("continue:" + request.requestId().value()),
                    request.sessionId(),
                    request.sessionVersion(),
                    request.assessmentResultId(),
                    OrchestrationOutcome.CONTINUE_CURRENT_NODE,
                    request.currentNodeId()
            );
        }

        var decision = result.decision().orElseThrow();
        var mappedId = new DecisionId(decision.decisionId().value());

        if (decision.status() == DecisionStatus.NO_CANDIDATE_AVAILABLE) {
            if (result.route() == OrchestrationRoute.NEXT_LEARNING_NODE && result.progress().completed()) {
                return new SessionOrchestrationDecision(mappedId, request.sessionId(), request.sessionVersion(), request.assessmentResultId(), OrchestrationOutcome.COMPLETED, null);
            }
            return new SessionOrchestrationDecision(mappedId, request.sessionId(), request.sessionVersion(), request.assessmentResultId(), OrchestrationOutcome.NO_CANDIDATE, null);
        }

        if (decision.status() != DecisionStatus.SELECTED || decision.selectedNodeId() == null) {
            throw new IllegalStateException("Tutor Orchestrator returned an unsupported decision status");
        }

        return new SessionOrchestrationDecision(
                mappedId,
                request.sessionId(),
                request.sessionVersion(),
                request.assessmentResultId(),
                OrchestrationOutcome.NEXT_NODE,
                new NodeId(decision.selectedNodeId().value())
        );
    }
}
