package com.aigora.tutororchestrator.application.contracts.result;
import com.aigora.tutororchestrator.application.error.SessionError;
import com.aigora.tutororchestrator.shared.validation.Require;
public record SessionFailure<T>(SessionError error) implements SessionResult<T> { public SessionFailure{Require.nonNull(error,"SessionError");} public boolean isSuccess(){return false;} public T value(){return null;} }
