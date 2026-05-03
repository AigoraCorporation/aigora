// Curriculum Graph — Neo4j Indexes
// These indexes support efficient lookups and traversal queries.
// All statements use IF NOT EXISTS for re-runnable/idempotent execution.

// Concept: index on domain for filtered traversal
CREATE INDEX concept_domain_idx IF NOT EXISTS
FOR (n:Concept) ON (n.domain);

// Concept: index on name for human-readable lookups
CREATE INDEX concept_name_idx IF NOT EXISTS
FOR (n:Concept) ON (n.name);

// CurriculumProfile: index on name
CREATE INDEX profile_name_idx IF NOT EXISTS
FOR (p:CurriculumProfile) ON (p.name);
