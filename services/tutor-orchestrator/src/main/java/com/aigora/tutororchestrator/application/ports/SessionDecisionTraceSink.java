package com.aigora.tutororchestrator.application.ports;
import com.aigora.tutororchestrator.application.context.SessionOrchestrationDecision;
public interface SessionDecisionTraceSink { void record(SessionOrchestrationDecision decision); }
