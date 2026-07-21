package com.aigora.tutororchestrator.application.contracts.result;

/**
 * Identifies the deterministic route followed by the orchestration pipeline.
 */
public enum OrchestrationRoute {

    LEARNING_IN_PROGRESS,
    NEXT_LEARNING_NODE,
    REGRESSION_NODE
}