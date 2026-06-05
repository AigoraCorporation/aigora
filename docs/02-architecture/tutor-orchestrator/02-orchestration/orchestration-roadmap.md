# Orchestration Roadmap

## Overview

This document centralizes the future evolution path of the Tutor Orchestrator architecture.

The current architecture is deterministic-first. Future capabilities must evolve on top of deterministic governance rather than bypassing it.

---

# Evolution Stages

```mermaid
flowchart LR

core["Deterministic Core"]
student["Student-Aware Orchestration"]
hybrid["Hybrid Orchestration"]
adaptive["Adaptive / AI-Assisted Orchestration"]

core --> student
student --> hybrid
hybrid --> adaptive
```

---

# Near-Term Evolution

- graph-only candidate generation
- deterministic policies
- deterministic ranking
- deterministic selection
- auditability foundations
- contract-based integration

---

# Future Capabilities

- student-aware orchestration
- hybrid orchestration
- heuristic-assisted ranking
- adaptive learning progression
- AI-assisted recommendation strategies
- semantic orchestration evaluation
- distributed event coordination
- advanced observability

---

# Governance Constraint

Every future orchestration capability must preserve:

- deterministic governance
- orchestration auditability
- bounded context isolation
- reproducible decision-making
- pedagogical consistency
