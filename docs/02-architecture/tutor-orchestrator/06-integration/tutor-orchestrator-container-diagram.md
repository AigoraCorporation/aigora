# Tutor Orchestrator Container Diagram

## Overview

This document describes the high-level container architecture of the AIGORA Tutor Orchestrator ecosystem.

---

# Container Diagram

The container architecture separates pedagogical orchestration from curriculum topology management through explicit gRPC service boundaries.

This separation preserves bounded context isolation, infrastructure encapsulation, and deterministic orchestration governance.

```mermaid
flowchart LR

student["Student / Client"]
orchestrator["Tutor Orchestrator<br/>(Java Service)"]
contracts["gRPC Contracts<br/>(Protobuf Boundary)"]
x["Curriculum Graph API<br/>(Python gRPC Service)"]
neo4j["Neo4j<br/>(Graph Database)"]

student --> orchestrator
orchestrator -->|gRPC| contracts
contracts --> x
x --> neo4j
```

---

# Architectural Responsibilities

* Tutor Orchestrator owns pedagogical decision-making.
* Curriculum Graph API owns graph traversal and topology access.
* Neo4j remains encapsulated behind the Curriculum Graph API.
* Communication occurs through explicit gRPC contracts.
* Tutor Orchestrator never queries Neo4j directly.

---

# Design Principle

The architecture separates educational orchestration from curriculum topology management to reduce coupling, improve scalability, and preserve bounded context ownership.
