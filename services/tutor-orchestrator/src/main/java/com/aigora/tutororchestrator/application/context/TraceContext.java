package com.aigora.tutororchestrator.application.context;

import com.aigora.tutororchestrator.domain.valueobjects.*;

public record TraceContext(
        CorrelationId correlationId,
        CausationId causationId
) {
}