package com.aigora.tutororchestrator.infrastructure;
import com.aigora.tutororchestrator.application.ports.*;import com.aigora.tutororchestrator.domain.model.*;import com.aigora.tutororchestrator.domain.valueobjects.*;import java.util.*;import java.util.concurrent.ConcurrentHashMap;
public final class InMemoryLearningSessionRepository implements LearningSessionRepository {
 private final Map<LearningSessionId,LearningSession> store=new ConcurrentHashMap<>();
 public Optional<LearningSession> findById(LearningSessionId id){var s=store.get(id);return Optional.ofNullable(s==null?null:s.copy());}
 public synchronized void insert(LearningSession session){if(store.containsKey(session.id())) throw new IllegalStateException("Learning session already exists");store.put(session.id(),session.copy());}
 public synchronized void update(LearningSession session, SessionVersion expectedVersion){var current=store.get(session.id());if(current==null)throw new IllegalStateException("Learning session not found");if(!current.version().equals(expectedVersion))throw new SessionVersionConflictException(session.id(),expectedVersion,current.version());store.put(session.id(),session.copy());}
 public List<LearningSession> findByStatus(LearningSessionStatus status){return store.values().stream().filter(s->s.status()==status).map(LearningSession::copy).toList();}
}
