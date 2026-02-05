# LinkedIn Post Draft

---

**Grounding AI reasoning in conflict analysis — deterministically, auditable, reproducible.**

We keep asking LLMs to *reason* about conflicts, negotiations, and complex disputes. They respond with fluent narratives — but the reasoning is opaque. No provenance. No deterministic logic. No audit trail.

**That is not analysis. That is narration.**

So we built a different approach at TACITUS:

- Use an LLM strictly for **structured extraction** (actors, events, claims, relationships, evidence)
- Store everything in a **knowledge graph** with source-span provenance
- Run **deterministic algorithms** for reasoning:
  - Contradictions → cosine similarity + negation analysis
  - Influence → PageRank on relationship networks
  - Issues → hierarchical clustering on claim embeddings
  - Entity resolution → fuzzy string matching

Same inputs → same outputs. Every conclusion is **traceable, reproducible, and falsifiable**.

**Why this matters:**

When analysis has consequences — diplomatic conflict, legal disputes, human friction — you need to know *why* the system concluded what it did. Deterministic grounding lets you challenge, inspect, and improve the logic instead of trusting a black box.

**We open-sourced a simplified, publishable reference pipeline.**

It mirrors how TACITUS structures grounded reasoning but in a compact, customizable form so you can:
- Tweak the **ontology** for your domain
- Swap extractors, resolvers, and graph logic
- Experiment with deterministic grounding on real conflict data

If you're exploring how to **ground LLM reasoning in a deterministic way**, this repo is a clean starting point:

github.com/sargonxg/TACITUS-Knowledge-Pipeline-open

---

**Shorter version (for higher engagement):**

---

LLMs generate. They don’t reason.

So we separated extraction from reasoning:

1. LLM extracts structured entities + evidence
2. Knowledge graph stores provenance
3. Deterministic algorithms do the reasoning

Same inputs → same outputs. Every conclusion traceable.

We open-sourced a simplified, customizable TACITUS pipeline to test grounded AI conflict reasoning in the real world.

github.com/sargonxg/TACITUS-Knowledge-Pipeline-open

#AI #KnowledgeGraphs #LLM #DeterministicAI #ConflictAnalysis #GraphRAG #Ontology #OpenSource

---

**Image suggestion:** Use the `tacitus-network.png` knowledge graph visualization as the post image.
