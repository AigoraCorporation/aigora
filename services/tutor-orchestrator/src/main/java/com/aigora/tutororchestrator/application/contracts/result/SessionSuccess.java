package com.aigora.tutororchestrator.application.contracts.result;
import com.aigora.tutororchestrator.application.error.SessionError;
public record SessionSuccess<T>(T value) implements SessionResult<T> { public boolean isSuccess(){return true;} public SessionError error(){return null;} }
