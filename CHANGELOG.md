# Changelog

All notable changes to this project will be documented in this file.

## [v0.3.0] - 2026-07-21

### Added

* Added the Tutor Orchestrator Core.
* Added a deterministic orchestration pipeline.
* Added the Decision Engine for pedagogical decision making.
* Added candidate generation and ranking pipeline.
* Added policy-based orchestration framework.
* Added Eligibility, Regression and Completion policies.
* Added Curriculum Graph integration contracts.
* Added gRPC adapter architecture.
* Added orchestration domain model.
* Added orchestration error model.
* Added shared validation utilities.
* Added observability foundations.
* Added testing infrastructure.


### Changed

* Changed the orchestration architecture to follow a deterministic-first approach.
* Improved separation between application, domain and infrastructure layers.
* Improved dependency injection configuration.
* Improved project documentation and architecture guides.


### Fixed

* Fixed decision reason modeling.
* Fixed orchestration validation consistency.
* Fixed dependency validation across the orchestration pipeline.

### Removed

* Removed experimental orchestration assumptions from the initial prototype.

---

## [v0.2.1] - 2026-05-15

### Added

* Neo4j persistence layer for Curriculum Graph
* Graph publication pipeline from canonical artifacts to Neo4j
* Idempotent graph loading strategy
* Neo4j constraints and index definitions
* Structural validation flow for persisted graph state
* Initial graph change management strategy
* Persistence validation architecture
* Graph synchronization and loading documentation
* Architecture Decision Records (ADR) structure

### Changed

* Transitioned Curriculum Graph from logical-only architecture to persistent graph infrastructure
* Refined separation between domain, application, and infrastructure responsibilities
* Improved alignment between domain entities and persistence schema
* Standardized graph publication orchestration through application use cases
* Refined validation responsibilities across structural, semantic, and operational layers
* Improved architectural documentation structure and navigation

### Fixed

* Inconsistencies between persistence model and canonical graph structure
* Broken or outdated architectural documentation references
* Misaligned terminology between graph artifacts and persistence layer

### Removed

* Early persistence assumptions from conceptual documentation
* Redundant graph publication flows from initial architecture drafts

---

## [v0.2.0] - 2026-04-24

### Added
- Curriculum Graph domain model definition
- Neo4j schema specification for Curriculum Graph
- Cypher query model for graph interaction
- Integration model between core components
- Architectural overview refinement for Curriculum Graph
- Consolidated documentation structure for curriculum graph module

### Changed
- Transitioned project from conceptual design to structured architecture
- Improved consistency across Curriculum Graph documentation
- Refined architectural boundaries between core components
- Standardized terminology and naming across documents

### Fixed
- Inconsistencies between domain model and supporting documentation
- Broken or misaligned internal documentation references

### Removed
- Redundant or outdated documentation fragments related to early design phase

---

## [v0.1.1] - 2026-03-27

### Added
- Release roadmap table for version planning
- Release issue template for structured release management
- Changelog CI workflow for automated changelog generation/update

### Changed
- Standardized release planning structure across repository
- Improved documentation organization for releases and versioning
- Updated .github templates structure (including pull request template)

### Fixed
- Inconsistent repository structure for GitHub templates

### Removed
- Duplicated content across documentation

---

## [v0.1.0] - 2026-03-13

### Added
- Assessment Engine documentation
- Retrieval Layer documentation
- LLM Gateway documentation

### Changed
- Tutor Orchestrator documentation refined
- Student Model specification improved
- Curriculum Graph documentation extended

### Fixed
- Internal documentation links
- Architecture overview consistency

### Removed
- Outdated constraints.md file