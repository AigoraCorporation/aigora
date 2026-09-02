package com.aigora.tutororchestrator.application.usecase;
import com.aigora.tutororchestrator.application.error.*; import com.aigora.tutororchestrator.application.contracts.result.*;
final class UseCaseSupport { private UseCaseSupport(){} static <T> SessionFailure<T> failure(SessionErrorCode code,String message){return new SessionFailure<>(new SessionError(code,message));} }
