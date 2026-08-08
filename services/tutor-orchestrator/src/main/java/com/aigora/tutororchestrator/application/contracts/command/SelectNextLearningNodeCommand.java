package com.aigora.tutororchestrator.application.contracts.command;

import com.aigora.tutororchestrator.application.context.OrchestrationContext;
import com.aigora.tutororchestrator.domain.valueobjects.NodeId;

public record SelectNextLearningNodeCommand(
        OrchestrationContext context,
        NodeId currentNodeId
) {
    public SelectNextLearningNodeCommand {
        if (context == null) {
            throw new IllegalArgumentException("OrchestrationContext must not be null");
        }
        if (currentNodeId == null) {
            throw new IllegalArgumentException("CurrentNodeId must not be null");
        }
    }
}
