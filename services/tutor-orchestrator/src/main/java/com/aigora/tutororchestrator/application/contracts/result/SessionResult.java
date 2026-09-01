package com.aigora.tutororchestrator.application.contracts.result;
import com.aigora.tutororchestrator.application.error.SessionError;
public sealed interface SessionResult<T> permits SessionSuccess, SessionFailure { boolean isSuccess(); T value(); SessionError error(); }
