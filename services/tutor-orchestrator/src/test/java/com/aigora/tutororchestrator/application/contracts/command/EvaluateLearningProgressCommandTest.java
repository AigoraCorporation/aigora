package com.aigora.tutororchestrator.application.contracts.command;

import com.aigora.tutororchestrator.application.context.OrchestrationContext;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;
import org.junit.jupiter.api.Test;

import static com.aigora.tutororchestrator.testsupport.builder.CommandBuilder.aCommand;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class EvaluateLearningProgressCommandTest {

    @Test
    void shouldCreateCommand() {
        OrchestrationContext context = aCommand().buildOrchestrationContext();
        NodeId currentNodeId = new NodeId("node-001");

        var command = new EvaluateLearningProgressCommand(
                context,
                currentNodeId
        );

        assertEquals(context, command.context());
        assertEquals(currentNodeId, command.currentNodeId());
    }

    @Test
    void shouldCompareByValue() {
        var first = new EvaluateLearningProgressCommand(
                aCommand().buildOrchestrationContext(),
                new NodeId("node-001")
        );

        var second = new EvaluateLearningProgressCommand(
                aCommand().buildOrchestrationContext(),
                new NodeId("node-001")
        );

        assertEquals(first, second);
    }

    @Test
    void shouldRejectNullContext() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new EvaluateLearningProgressCommand(
                        null,
                        new NodeId("node-001")
                )
        );
    }

    @Test
    void shouldRejectNullCurrentNodeId() {
        assertThrows(
                IllegalArgumentException.class,
                () -> new EvaluateLearningProgressCommand(
                        aCommand().buildOrchestrationContext(),
                        null
                )
        );
    }
}
