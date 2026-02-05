# LinkedIn Post Draft

---

**Why I stopped asking LLMs to reason — and started building graphs instead.**

We've been using AI wrong for analysis.

We feed an LLM a 50-page report and ask: "Who are the key actors? What are the contradictions? Who holds leverage?" And the model gives us a polished answer. Fluent. Confident. Unverifiable.

That's not analysis. That's narration.

Here's the problem: LLMs reason by predicting the next token. They don't track provenance. They don't flag contradictions unless they happen to notice. They can't tell you *why* they concluded that Actor X opposes Actor Y — because they didn't reason to that conclusion. They generated it.

**So we built something different.**

TACITUS is a knowledge graph pipeline that uses LLMs for what they're actually good at — structured extraction — then performs reasoning deterministically over a graph.

The key insight: **separate extraction from reasoning.**

- The LLM extracts actors, events, claims, relationships, and evidence from unstructured text
- A knowledge graph stores them with full provenance (every claim links to a source text span)
- Deterministic algorithms do the actual reasoning:
  - **Contradiction detection** via cosine similarity + negation analysis
  - **Influence scoring** via PageRank on actor-relationship networks
  - **Issue clustering** via agglomerative clustering on claim embeddings
  - **Entity resolution** via fuzzy string matching

No temperature sampling. No hidden weights making the decision. Same inputs → same outputs. Every conclusion is traceable, reproducible, and falsifiable.

**Why does this matter?**

When the analysis has consequences — geopolitical intelligence, legal disputes, conflict mediation — you need to know:
- Where did this conclusion come from?
- What evidence supports it?
- Can I challenge it?

With a raw LLM, the answer to all three is "no." With a knowledge graph, every node traces back to a source document, a specific text span, and a confidence score.

**We just open-sourced the pipeline.**

It's a working implementation in Python: Gemini 1.5 Pro for extraction, Neo4j for the graph, FAISS for vector search, Pydantic for schema validation, NetworkX for graph algorithms.

It includes theory-guided extraction (we call it OntoRAG) — the system seeds the graph with established conflict theories and selects the most relevant ones before each extraction, so the LLM gets targeted analytical context instead of a generic prompt.

This is a small open-source piece of what TACITUS does. We think knowledge graphs + structured extraction is the future of AI reasoning for high-stakes domains. Not because LLMs aren't powerful — but because powerful generation without grounding isn't analysis.

Check it out: github.com/sargonxg/TACITUS-Knowledge-Pipeline-open

---

**Shorter version (for higher engagement):**

---

LLMs don't reason. They generate.

Ask GPT/Claude/Gemini to analyze a conflict and you get fluent, confident, unverifiable narration.

So we stopped asking LLMs to reason. We built a knowledge graph pipeline instead:

1. LLM extracts structured entities (actors, claims, events, evidence)
2. Knowledge graph stores them with full provenance
3. **Deterministic algorithms** do the actual reasoning:
   - Contradictions → cosine similarity + negation analysis
   - Influence → PageRank on relationship networks
   - Issues → hierarchical clustering on claim embeddings

Same inputs. Same outputs. Every conclusion traceable. No black boxes.

We call it TACITUS. Just open-sourced the pipeline.

github.com/sargonxg/TACITUS-Knowledge-Pipeline-open

#AI #KnowledgeGraphs #NLP #LLM #OpenSource #ConflictAnalysis #Neo4j #DeterministicAI

---

**Image suggestion:** Use the `tacitus-network.png` knowledge graph visualization as the post image. The dense, interconnected graph is visually striking and immediately communicates the concept.
