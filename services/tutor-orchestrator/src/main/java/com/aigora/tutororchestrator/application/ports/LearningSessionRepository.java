package com.aigora.tutororchestrator.application.ports;
import com.aigora.tutororchestrator.domain.model.*; import com.aigora.tutororchestrator.domain.valueobjects.*; import java.util.*;
public interface LearningSessionRepository { Optional<LearningSession> findById(LearningSessionId id); void insert(LearningSession session); void update(LearningSession session, SessionVersion expectedVersion); List<LearningSession> findByStatus(LearningSessionStatus status); }
