package com.aigora.tutororchestrator.application.error;
import com.aigora.tutororchestrator.shared.validation.Require;
public record SessionError(SessionErrorCode code, String message) { public SessionError { Require.nonNull(code,"SessionErrorCode"); message=Require.nonBlank(message,"message"); } }
