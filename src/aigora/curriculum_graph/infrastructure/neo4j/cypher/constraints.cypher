// Curriculum Graph — Neo4j Uniqueness Constraints
// These constraints ensure idempotent MERGE operations and prevent duplicates.
// All statements use IF NOT EXISTS for re-runnable/idempotent execution.

// Concept node: unique by id
CREATE CONSTRAINT concept_id_unique IF NOT EXISTS
FOR (n:Concept) REQUIRE n.id IS UNIQUE;

// CurriculumProfile node: unique by id
CREATE CONSTRAINT profile_id_unique IF NOT EXISTS
FOR (p:CurriculumProfile) REQUIRE p.id IS UNIQUE;

// GraphMetadata node: single active-snapshot marker, unique by key (ADR-007)
CREATE CONSTRAINT graph_metadata_key_unique IF NOT EXISTS
FOR (m:GraphMetadata) REQUIRE m.key IS UNIQUE;
