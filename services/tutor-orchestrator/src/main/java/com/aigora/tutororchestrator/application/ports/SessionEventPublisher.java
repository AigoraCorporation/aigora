package com.aigora.tutororchestrator.application.ports;
import com.aigora.tutororchestrator.domain.model.SessionEvent; import java.util.List;
public interface SessionEventPublisher { void publish(List<SessionEvent> events); }
