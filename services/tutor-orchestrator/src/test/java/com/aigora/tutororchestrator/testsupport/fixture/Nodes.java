package com.aigora.tutororchestrator.testsupport.fixture;

import com.aigora.tutororchestrator.domain.valueobjects.NodeId;

public final class Nodes {

    public static final NodeId CURRENT_NODE = new NodeId("node-001");
    public static final NodeId NEXT_NODE = new NodeId("node-002");
    public static final NodeId REVIEW_NODE = new NodeId("node-003");
    public static final NodeId REGRESSION_NODE = new NodeId("node-prerequisite-001");

    private Nodes() {
    }
}