package com.aigora.tutororchestrator.testsupport.builder;

import com.aigora.tutororchestrator.application.context.DecisionEvidenceContext;
import com.aigora.tutororchestrator.application.context.LearningSessionReference;
import com.aigora.tutororchestrator.application.context.OrchestrationContext;
import com.aigora.tutororchestrator.application.context.TraceContext;
import com.aigora.tutororchestrator.application.contracts.command.EvaluateLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectNextLearningNodeCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectRegressionNodeCommand;
import com.aigora.tutororchestrator.domain.valueobjects.AssessmentResultId;
import com.aigora.tutororchestrator.domain.valueobjects.CausationId;
import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.ExerciseAttemptId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.LearningSessionId;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.OrchestrationRequestId;
import com.aigora.tutororchestrator.domain.valueobjects.PolicySetVersion;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentModelVersion;

public final class CommandBuilder {

    private StudentId studentId = new StudentId("student-001");
    private NodeId currentNodeId = new NodeId("node-001");
    private GraphVersion graphVersion = new GraphVersion("v1.0.0");
    private CorrelationId correlationId = new CorrelationId("corr-001");
    private LearningSessionId learningSessionId = new LearningSessionId("session-001");
    private ExerciseAttemptId exerciseAttemptId = new ExerciseAttemptId("attempt-001");
    private AssessmentResultId assessmentResultId = new AssessmentResultId("assessment-001");
    private StudentModelVersion studentModelVersion = new StudentModelVersion("student-model-v1");
    private PolicySetVersion policySetVersion = new PolicySetVersion("policy-set-v1");
    private OrchestrationRequestId requestId = new OrchestrationRequestId("request-001");
    private CausationId causationId = new CausationId("cause-001");

    private CommandBuilder() {
    }

    public static CommandBuilder aCommand() {
        return new CommandBuilder();
    }

    public CommandBuilder withStudentId(String studentId) {
        this.studentId = new StudentId(studentId);
        return this;
    }

    public CommandBuilder withCurrentNodeId(String currentNodeId) {
        this.currentNodeId = new NodeId(currentNodeId);
        return this;
    }

    public CommandBuilder withGraphVersion(String graphVersion) {
        this.graphVersion = new GraphVersion(graphVersion);
        return this;
    }

    public CommandBuilder withCorrelationId(String correlationId) {
        this.correlationId = new CorrelationId(correlationId);
        return this;
    }

    public OrchestrationContext buildOrchestrationContext() {
        return new OrchestrationContext(
                requestId,
                studentId,
                new LearningSessionReference(
                        learningSessionId,
                        exerciseAttemptId
                ),
                new DecisionEvidenceContext(
                        assessmentResultId,
                        studentModelVersion,
                        graphVersion,
                        policySetVersion
                ),
                new TraceContext(
                        correlationId,
                        causationId
                )
        );
    }

    public SelectNextLearningNodeCommand buildSelectNextLearningNodeCommand() {
        return new SelectNextLearningNodeCommand(
                buildOrchestrationContext(),
                currentNodeId
        );
    }

    public SelectRegressionNodeCommand buildSelectRegressionNodeCommand() {
        return new SelectRegressionNodeCommand(
                buildOrchestrationContext(),
                currentNodeId
        );
    }

    public EvaluateLearningProgressCommand buildEvaluateLearningProgressCommand() {
        return new EvaluateLearningProgressCommand(
                buildOrchestrationContext(),
                currentNodeId
        );
    }
}
