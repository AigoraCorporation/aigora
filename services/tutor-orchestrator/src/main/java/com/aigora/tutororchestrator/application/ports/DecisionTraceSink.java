package com.aigora.tutororchestrator.application.ports;

import com.aigora.tutororchestrator.domain.model.OrchestrationDecision;

/**
 * Outbound application port responsible for recording completed
 * orchestration decisions and their associated decision trace.
 *
 * <p>The port intentionally exposes no persistence, messaging, or
 * observability technology. Adapters decide how the evidence is stored
 * or forwarded.</p>
 */
public interface DecisionTraceSink {

    void record(OrchestrationDecision decision);
}