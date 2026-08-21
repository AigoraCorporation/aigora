package com.aigora.tutororchestrator.application.ports;
import com.aigora.tutororchestrator.domain.valueobjects.*;
public interface LifecycleTelemetrySink { void record(String operation, LearningSessionId sessionId, SessionVersion version, String outcome, long durationNanos); }
