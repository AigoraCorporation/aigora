package com.aigora.tutororchestrator.domain.policy;

public final class CompletionPolicy {

    public boolean isCompleted(boolean masteredCurrentNode) {
        return masteredCurrentNode;
    }
}