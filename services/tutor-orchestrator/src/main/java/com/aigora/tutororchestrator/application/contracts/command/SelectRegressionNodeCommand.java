package com.aigora.tutororchestrator.application.contracts.command;

import com.aigora.tutororchestrator.application.context.OrchestrationContext;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;

/**
 * Command used to select a regression node for the current orchestration
 * execution.
 *
 * @param context immutable orchestration context
 * @param currentNodeId node from which regression is evaluated
 */
public record SelectRegressionNodeCommand(
        OrchestrationContext context,
        NodeId currentNodeId
) {

    public SelectRegressionNodeCommand {
        if (context == null) {
            throw new IllegalArgumentException(
                    "OrchestrationContext must not be null"
            );
        }

        if (currentNodeId == null) {
            throw new IllegalArgumentException(
                    "NodeId must not be null"
            );
        }
    }
}