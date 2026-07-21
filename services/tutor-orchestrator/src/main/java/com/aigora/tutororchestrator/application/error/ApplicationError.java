package com.aigora.tutororchestrator.application.error;

/**
 * Stable application-level representation of an orchestration failure.
 *
 * <p>Implementations must not expose transport, infrastructure, gRPC,
 * protobuf, HTTP, networking, or persistence-specific types.</p>
 */
public sealed interface ApplicationError
        permits GraphUnavailable,
                InvalidGraphResponse,
                NoCandidateAvailable,
                DependencyTimeout,
                StudentModelUnavailable,
                AssessmentUnavailable {

    ApplicationErrorCode code();

    String message();
}