/**
 * Application layer of the AIGORA Tutor Orchestrator.
 *
 * <p>This layer coordinates deterministic orchestration use cases and defines
 * the boundaries through which external capabilities are consumed.</p>
 *
 * <p>It may depend on the domain layer, but it must not depend on transport,
 * persistence, gRPC, protobuf, HTTP, Spring, or other infrastructure-specific
 * technologies.</p>
 */
package com.aigora.tutororchestrator.application;