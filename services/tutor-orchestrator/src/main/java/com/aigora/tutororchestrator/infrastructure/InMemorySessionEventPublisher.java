package com.aigora.tutororchestrator.infrastructure;
import com.aigora.tutororchestrator.application.ports.SessionEventPublisher;import com.aigora.tutororchestrator.domain.model.SessionEvent;import java.util.*;
public final class InMemorySessionEventPublisher implements SessionEventPublisher {private final List<SessionEvent> events=new ArrayList<>();public synchronized void publish(List<SessionEvent> batch){events.addAll(List.copyOf(batch));}public synchronized List<SessionEvent> publishedEvents(){return List.copyOf(events);} }
