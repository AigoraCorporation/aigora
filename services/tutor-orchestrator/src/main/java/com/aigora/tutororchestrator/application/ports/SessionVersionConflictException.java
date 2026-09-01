package com.aigora.tutororchestrator.application.ports;
import com.aigora.tutororchestrator.domain.valueobjects.*;
public final class SessionVersionConflictException extends RuntimeException { public SessionVersionConflictException(LearningSessionId id, SessionVersion expected, SessionVersion actual){super("Session version conflict for " + id + ": expected " + expected.value() + " but was " + actual.value());} }
