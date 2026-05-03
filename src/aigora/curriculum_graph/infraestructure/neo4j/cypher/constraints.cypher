// Curriculum Graph — Neo4j Uniqueness Constraints
// These constraints ensure idempotent MERGE operations and prevent duplicates.
// All statements use IF NOT EXISTS for re-runnable/idempotent execution.

// Concept node: unique by id
CREATE CONSTRAINT concept_id_unique IF NOT EXISTS
FOR (n:Concept) REQUIRE n.id IS UNIQUE;

// CurriculumProfile node: unique by id
CREATE CONSTRAINT profile_id_unique IF NOT EXISTS
FOR (p:CurriculumProfile) REQUIRE p.id IS UNIQUE;
