// Count all persisted Concept nodes.
// Returns: node_count AS INTEGER
MATCH (n:Concept) RETURN count(n) AS node_count;

// Count persisted PREREQUISITE_OF relationships between the given node IDs.
// Parameter: $ids — list of expected node IDs
// Returns: edge_count AS INTEGER
MATCH (src:Concept)-[r:PREREQUISITE_OF]->(tgt:Concept)
WHERE src.id IN $ids AND tgt.id IN $ids
RETURN count(r) AS edge_count;

// Check which node IDs from the provided list are persisted.
// Parameter: $ids — list of expected node IDs
// Returns: found_id AS STRING (one row per found node)
UNWIND $ids AS id MATCH (n:Concept {id: id}) RETURN n.id AS found_id;

// Check which profile IDs from the provided list are persisted.
// Parameter: $ids — list of expected profile IDs
// Returns: found_id AS STRING (one row per found profile)
UNWIND $ids AS id MATCH (p:CurriculumProfile {id: id}) RETURN p.id AS found_id;
