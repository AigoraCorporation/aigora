package com.aigora.tutororchestrator.testsupport.builder;

import com.aigora.tutororchestrator.application.contracts.command.EvaluateLearningProgressCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectNextLearningNodeCommand;
import com.aigora.tutororchestrator.application.contracts.command.SelectRegressionNodeCommand;
import com.aigora.tutororchestrator.domain.valueobjects.CorrelationId;
import com.aigora.tutororchestrator.domain.valueobjects.GraphVersion;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import com.aigora.tutororchestrator.domain.valueobjects.StudentId;

public final class CommandBuilder {

    private StudentId studentId = new StudentId("student-001");
    private NodeId currentNodeId = new NodeId("node-001");
    private GraphVersion graphVersion = new GraphVersion("v1.0.0");
    private CorrelationId correlationId = new CorrelationId("corr-001");

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

    public SelectNextLearningNodeCommand buildSelectNextLearningNodeCommand() {
        return new SelectNextLearningNodeCommand(
                studentId,
                currentNodeId,
                graphVersion,
                correlationId
        );
    }

    public SelectRegressionNodeCommand buildSelectRegressionNodeCommand() {
    return new SelectRegressionNodeCommand(
            studentId,
            currentNodeId,
            graphVersion,
            correlationId
    );
    }

    public EvaluateLearningProgressCommand buildEvaluateLearningProgressCommand() {
    return new EvaluateLearningProgressCommand(
            studentId,
            currentNodeId,
            graphVersion,
            correlationId
    );
    }

}