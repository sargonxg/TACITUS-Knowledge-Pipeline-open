# TACITUS Cypher Query Library

Ready-to-use queries for exploring TACITUS knowledge graphs in Neo4j Browser.

Replace `$case_id` with your actual case ID, or use a parameter in Neo4j Browser.

---

## Actor Analysis

### All actors with roles
```cypher
MATCH (c:Case)-[:CONTAINS]->(a:Actor)
WHERE c.entity_id = $case_id
RETURN a.name AS actor, a.actor_type AS type, a.role AS role,
       a.is_primary AS primary, a.confidence AS confidence
ORDER BY a.is_primary DESC, a.name
```

### Actor relationship network
```cypher
MATCH (a:Actor)-[r]->(b:Actor)
WHERE a.case_id = $case_id
  AND type(r) IN ['OPPOSES', 'ALLIES_WITH', 'INFLUENCES', 'DEPENDS_ON']
RETURN a.name AS from_actor, type(r) AS relationship,
       b.name AS to_actor, r.description AS context
ORDER BY type(r), a.name
```

### Opposing actors (conflicts)
```cypher
MATCH (a:Actor)-[r:OPPOSES]->(b:Actor)
WHERE a.case_id = $case_id
RETURN a.name AS actor, b.name AS opponent,
       r.description AS conflict_description
ORDER BY a.name
```

### Allied actors (alliances)
```cypher
MATCH (a:Actor)-[r:ALLIES_WITH]->(b:Actor)
WHERE a.case_id = $case_id
RETURN a.name AS actor, b.name AS ally,
       r.description AS alliance_basis
ORDER BY a.name
```

### Most connected actors (degree centrality)
```cypher
MATCH (a:Actor)
WHERE a.case_id = $case_id
OPTIONAL MATCH (a)-[r]-()
WITH a, count(r) AS degree
RETURN a.name AS actor, a.role AS role, degree
ORDER BY degree DESC
LIMIT 15
```

### Influence scores (after PageRank)
```cypher
MATCH (a:Actor)
WHERE a.case_id = $case_id AND a.influence_score IS NOT NULL
RETURN a.name AS actor, a.role AS role,
       round(a.influence_score, 4) AS influence_score
ORDER BY a.influence_score DESC
LIMIT 10
```

---

## Event Timeline

### Full event timeline
```cypher
MATCH (e:Event)
WHERE e.case_id = $case_id
RETURN e.date AS date, e.description AS event,
       e.event_type AS type, e.impact AS impact
ORDER BY e.date
```

### Critical events only
```cypher
MATCH (e:Event)
WHERE e.case_id = $case_id AND e.impact = 'critical'
RETURN e.date AS date, e.description AS event,
       e.event_type AS type
ORDER BY e.date
```

### Events by actor
```cypher
MATCH (a:Actor)-[:INITIATES_EVENT]->(e:Event)
WHERE a.case_id = $case_id
RETURN a.name AS actor, e.date AS date,
       e.description AS event, e.impact AS impact
ORDER BY e.date
```

---

## Claims & Evidence

### All claims by actor
```cypher
MATCH (a:Actor)-[:MAKES_CLAIM]->(c:Claim)
WHERE a.case_id = $case_id
RETURN a.name AS actor, c.claim_type AS type,
       c.statement AS claim, c.confidence AS confidence
ORDER BY a.name, c.confidence DESC
```

### Trace claims to source evidence
```cypher
MATCH (a:Actor)-[:MAKES_CLAIM]->(c:Claim)-[:SUPPORTED_BY]->(s:Span)
WHERE c.case_id = $case_id
RETURN a.name AS actor, c.statement AS claim,
       s.quote AS source_evidence,
       s.start AS char_offset, s.score AS match_confidence
ORDER BY s.score DESC
```

### Claims without evidence (quality check)
```cypher
MATCH (c:Claim)
WHERE c.case_id = $case_id
  AND NOT (c)-[:SUPPORTED_BY]->(:Span)
RETURN c.actor AS actor, c.statement AS unsupported_claim,
       c.confidence AS confidence
ORDER BY c.confidence DESC
```

---

## Contradiction Detection

### All detected contradictions
```cypher
MATCH (c1:Claim)-[r:POTENTIAL_CONTRADICTION]->(c2:Claim)
WHERE c1.case_id = $case_id
RETURN c1.actor AS actor_1, c1.statement AS claim_1,
       c2.actor AS actor_2, c2.statement AS claim_2,
       round(r.similarity, 3) AS semantic_similarity,
       r.rationale AS detection_method
ORDER BY r.similarity DESC
```

### Contradictions by issue cluster
```cypher
MATCH (c1:Claim)-[r:POTENTIAL_CONTRADICTION]->(c2:Claim),
      (c1)-[:ABOUT_ISSUE]->(i:Issue)
WHERE c1.case_id = $case_id
RETURN i.issue_label AS issue,
       c1.actor AS actor_1, c1.statement AS claim_1,
       c2.actor AS actor_2, c2.statement AS claim_2,
       round(r.similarity, 3) AS similarity
ORDER BY i.issue_label, r.similarity DESC
```

---

## Interests & Leverage

### Actor interests
```cypher
MATCH (a:Actor)-[:HAS_INTEREST]->(i:Interest)
WHERE a.case_id = $case_id
RETURN a.name AS actor, i.interest_type AS type,
       i.description AS interest
ORDER BY a.name
```

### Leverage holdings
```cypher
MATCH (a:Actor)-[:HOLDS_LEVERAGE]->(l:Leverage)
WHERE a.case_id = $case_id
RETURN a.name AS actor, l.leverage_type AS type,
       l.description AS leverage
ORDER BY a.name
```

### Constraints on actors
```cypher
MATCH (a:Actor)-[:FACES_CONSTRAINT]->(c:Constraint)
WHERE a.case_id = $case_id
RETURN a.name AS actor, c.constraint_type AS type,
       c.description AS constraint
ORDER BY a.name
```

### Commitments between parties
```cypher
MATCH (a:Actor)-[:MADE_COMMITMENT]->(c:Commitment)
WHERE a.case_id = $case_id
RETURN a.name AS actor, c.target AS to_whom,
       c.description AS commitment, c.status AS status
ORDER BY c.status, a.name
```

---

## Issue Clustering

### All issue clusters with claim counts
```cypher
MATCH (i:Issue)
WHERE i.case_id = $case_id
OPTIONAL MATCH (c:Claim)-[:ABOUT_ISSUE]->(i)
WITH i, count(c) AS claim_count
RETURN i.issue_label AS issue, i.top_terms AS key_terms,
       claim_count
ORDER BY claim_count DESC
```

### Claims grouped by issue
```cypher
MATCH (c:Claim)-[:ABOUT_ISSUE]->(i:Issue)
WHERE c.case_id = $case_id
RETURN i.issue_label AS issue, c.actor AS actor,
       c.statement AS claim
ORDER BY i.issue_label, c.actor
```

---

## Grounding Theory (GND Layer)

### Seeded conflict theories
```cypher
MATCH (t:Theory)
RETURN t.name AS theory, t.description AS description,
       t.proponent AS proponent
ORDER BY t.name
```

### Causal chains in theory
```cypher
MATCH (a:Concept)-[r:CAUSAL_LINK]->(b:Concept)
RETURN a.name AS cause, r.relation_type AS relationship,
       b.name AS effect, round(r.confidence, 2) AS confidence,
       r.justification AS reasoning
ORDER BY r.confidence DESC
```

---

## Graph Health & Statistics

### Node counts by type
```cypher
MATCH (n)
WHERE n.case_id = $case_id
RETURN labels(n)[0] AS type, count(n) AS count
ORDER BY count DESC
```

### Orphan nodes (no relationships)
```cypher
MATCH (n)
WHERE n.case_id = $case_id AND NOT (n)--()
RETURN labels(n)[0] AS type, n.name AS name
ORDER BY type
```

### Full graph statistics
```cypher
MATCH (c:Case)
WHERE c.entity_id = $case_id
OPTIONAL MATCH (c)-[*1..2]->(n)
WITH c, labels(n)[0] AS type, count(n) AS cnt
RETURN c.name AS case_name, type, cnt
ORDER BY cnt DESC
```

---

## Semantic Search (Vector Queries)

### Find similar actors by embedding
```cypher
MATCH (a:Actor {name: $actor_name})
WITH a.embedding AS query_vec
CALL db.index.vector.queryNodes('actor_embedding', 5, query_vec)
YIELD node, score
WHERE node.name <> $actor_name
RETURN node.name AS similar_actor, node.role AS role,
       round(score, 3) AS similarity
```

### Natural language search across all entities
```cypher
WITH $query_embedding AS query_vec
CALL db.index.vector.queryNodes('entity_embedding', 10, query_vec)
YIELD node, score
RETURN labels(node)[0] AS type, node.name AS entity,
       round(score, 3) AS relevance
ORDER BY score DESC
```
