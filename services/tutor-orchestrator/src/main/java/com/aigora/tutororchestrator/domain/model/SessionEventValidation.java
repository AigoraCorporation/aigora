package com.aigora.tutororchestrator.domain.model;
import com.aigora.tutororchestrator.domain.valueobjects.*;import java.time.Instant;
final class SessionEventValidation {private SessionEventValidation(){}static void required(EventId e,LearningSessionId s,SessionVersion v,CorrelationId c,CausationId ca,Instant at){if(e==null||s==null||v==null||c==null||ca==null||at==null)throw new IllegalArgumentException("Session event metadata must not be null");}}
