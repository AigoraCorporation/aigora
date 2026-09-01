package com.aigora.tutororchestrator.application.ports;
import com.aigora.tutororchestrator.application.context.*;
public interface TutorOrchestratorClient { SessionOrchestrationDecision decide(SessionOrchestrationRequest request); }
