# Research for better AI knowledge generation

TACITUS develops and tests infrastructure for carrying evidence, context, qualifications and work products between conversations, people and agents. These releases make the methods and current evidence inspectable. Building a graph, retaining citations or saving tokens does not by itself establish better answers; quality, human effort and total cost need separate evaluation.

## Current papers · version 1.1

| Publication | Read and download | What the evidence supports |
| --- | --- | --- |
| **TAC-2026-01. TACITUS: Context Capsules, Artefacts, and Small Knowledge Graphs for AI Generation** | [Accessible reader](https://tacitus.me/research/context-capsules/paper/v1.1/) · [PDF](context-capsules/v1.1/tacitus-context-capsules-v1.1.pdf) · [Source and reproduction](context-capsules/v1.1/README.md) · [BibTeX](context-capsules/v1.1/citation.bib) | An architecture and controlled evaluation proposal with 21 references, executable context replay, and a real NIST source-edition case. Confirmatory efficacy studies are proposed, not preregistered or executed. |
| **WT-2026-01. Wind Tunnel: Evidence-Separated Population Modeling for AI-Assisted Research Preparation** | [Accessible reader](https://tacitus.me/research/wind-tunnel/paper/v1.1/) · [PDF](wind-tunnel-methodology/v1.1/wind-tunnel-methodology-v1.1.pdf) · [Source and reproduction](wind-tunnel-methodology/v1.1/README.md) · [BibTeX](wind-tunnel-methodology/v1.1/citation.bib) | A documented experimental procedure and a retrospective twelve-item GSS comparison. Mean TV is 2.48 pp for the 2022 persistence baseline, 7.50 for the national model, and 8.16 for the conditioned, weighted recipe. No mean improvement is established for the conditioned recipe. |

Both revisions are dated **24 November 2026** and published by TACITUS. They are not independently peer-reviewed and claim no journal acceptance or DOI registration. Capsule efficacy, questionnaire-preparation usefulness and representative opinion measurement are distinct research questions. Wind Tunnel's weighted human-survey reference is an estimate, not population truth; its national/cell comparison bundles prompting, call structure and weighting rather than isolating one component.

The papers preserve earlier observations and disclose commercial interests and AI assistance. Revision critiques, citation data, equations, vector figures, source identities and checksums accompany each release. [The TACITUS evaluation protocol](context-capsules/v1.1/evaluation-protocol.json) and [Wind Tunnel evaluation agenda](wind-tunnel-methodology/v1.1/evaluation-agenda.json) are proposals, not reported results.

## Source graph · AI governance

[Inspect the source-map release](ai-governance-source-map/v1/README.md) · [Graph JSON](ai-governance-source-map/v1/graph.json) · [Ontology](ai-governance-source-map/v1/ontology.json) · [Source lock](ai-governance-source-map/v1/source-lock.json) · [Records CSV](ai-governance-source-map/v1/records.csv)

The final graph contains **2,793 source-linked records and 4,517 typed links** from two pinned official adopted texts: the AI Act and GDPR. Those counts are computed from actual graph records and verified on rebuild. The map includes 212 articles, 353 recitals, 2,064 substantive passages and 94 document-specific definitions, plus document headings and annexes. Links distinguish published structure, lexical article/annex references, definitions and literal term mentions.

This larger source map supports inspecting and selecting a small task subgraph; it is not itself a task capsule or a complete legal ontology. Exact quotes, Unicode offsets, source editions, link methods and extraction limits travel with the data. The pinned adopted editions do not represent today's consolidated legal position. Reading presets are authored inspection questions, not approved legal conclusions. No private team discussions, fake review approvals or generation gains are bundled.

## Reproduce without inference

From the repository root, Python 3.11+ and Node.js 20+ are enough for the released-data checks. The verifiers make no model calls or downloads and need no credentials or third-party Python packages:

```sh
python research/context-capsules/v1/verify.py
python research/context-capsules/v1.1/verify.py
python research/wind-tunnel-methodology/v1/verify.py
python research/wind-tunnel-methodology/v1.1/verify.py
python research/ai-governance-source-map/v1/verify.py
```

[The research CI workflow](../.github/workflows/context-proposal.yml) runs the archived and current paper verifiers and the source-graph verifier. Paper checks cover manifest hashes, reference inputs, context/score replay, citation coverage, semantic HTML and mathematical displays. The source-map check performs a byte-for-byte reconstruction, verifies exact quotation spans, checks every relation domain/range, and retains regressions for cross-instrument scope and important qualifiers. Passing establishes the tested artifact and source-fidelity properties, not answer quality or expert approval.

To rebuild PDFs, install the additional Matplotlib/Pandoc/XeLaTeX toolchain documented in the paper directories. To rebuild the graph, run `python research/ai-governance-source-map/v1/build.py`; it uses only pinned local sources. New source editions belong in new version directories.

## Preserved publication history

- [TACITUS context capsules · v1.0](context-capsules/v1/README.md) · [original reader](https://tacitus.me/research/context-capsules/paper/)
- [Wind Tunnel methodology · v1.0](wind-tunnel-methodology/v1/README.md) · [original reader](https://tacitus.me/research/wind-tunnel/paper/)

The original releases, their PDFs and their manifests remain unchanged. Version 1.1 adds critique, sharper methods and interpretation, and improved research-use explanations; it does not convert unrun studies into results or replace the benchmark distributions.

## Reading index

A small, versioned reading index: primary paper links, the engineering question each raises, and the boundary between that research and this implementation. Reviewed 10 November 2026 at landing-page/abstract level. These are design references, not evidence that TACITUS reproduces their results. No copyrighted paper archive is bundled.

## Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

Lewis et al. · 2020 · [Primary source](https://arxiv.org/abs/2005.11401)

Separate model parameters from a retrievable evidence collection. The source register and bounded capsule are explicit non-parametric context. This reference does not implement the paper’s trained retriever.

## Lost in the Middle: How Language Models Use Long Contexts

Liu et al. · 2023 · [Primary source](https://arxiv.org/abs/2307.03172)

Evidence placement can affect retrieval from a long prompt. Bounded context and source selection need positional stress tests; shorter context alone is not an answer-quality metric.

## Enabling Large Language Models to Generate Text with Citations

Gao et al. · 2023 · [Primary source](https://aclanthology.org/2023.emnlp-main.398/)

Evaluate fluency, correctness and citation quality separately. generation.py checks reference integrity. It does not implement the paper’s entailment or full citation-quality evaluator.

## Measuring Attribution in Natural Language Generation Models

Rashkin et al. · 2023 · [Primary source](https://aclanthology.org/2023.cl-4.2/)

Attribution must be checked against an identified source. The workbench exposes each source passage for review; a valid evidence ID does not prove the associated paraphrase.

## FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation

Min et al. · 2023 · [Primary source](https://arxiv.org/abs/2305.14251)

A long answer can mix supported and unsupported claims. The draft uses individual cited items. No FActScore model judge or calibrated factuality score is claimed.

## Ragas: Automated Evaluation of Retrieval Augmented Generation

Es et al. · 2023 · [Primary source](https://arxiv.org/abs/2309.15217)

Retrieval and generation require distinct evaluation dimensions. Usage, reference checks and proposed domain rubrics are separate. This code does not run Ragas.

## ReAct: Synergizing Reasoning and Acting in Language Models

Yao et al. · 2022 · [Primary source](https://arxiv.org/abs/2210.03629)

Interleave model decisions with task-specific evidence access. agent.py allows inspect_evidence and draft under a finite step budget. It records actions, not hidden chain of thought, and does not reproduce the ReAct benchmark.

## Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection

Asai et al. · 2023 · [Primary source](https://arxiv.org/abs/2310.11511)

Retrieval and reflection can be made conditional on the task. A learned reflection policy is a research option, not implemented by the current fixed tool contract.

## From Local to Global: A Graph RAG Approach to Query-Focused Summarization

Edge et al. · 2024 · [Primary source](https://arxiv.org/abs/2404.16130)

Global corpus questions differ from retrieving one supporting passage. The present graph preserves provenance; it does not implement GraphRAG community summaries or establish corpus-wide completeness.

## HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models

Gutiérrez et al. · 2024 · [Primary source](https://arxiv.org/abs/2405.14831)

Knowledge graphs and graph-based retrieval can support multi-hop questions. Graph retrieval is an experimental extension. The local reference uses an authored semantic layer, not Personalized PageRank.

## RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval

Sarthi et al. · 2024 · [Primary source](https://arxiv.org/abs/2401.18059)

Multiple levels of summarization can support document retrieval. Candidate research for large corpora. Summaries would need their own source lineage; no recursive summarizer is implemented here.

## Attribution, Citation, and Quotation: A Survey of Evidence-based Text Generation with Large Language Models

Schreieder, Schopf and Färber · 2026 · [Primary source](https://aclanthology.org/2026.acl-long.1430/)

Treat attribution, citation and quotation as distinct evidence operations. The workflow separates exact quoted evidence, citation identity checks and an unverified model paraphrase.

## From legal workflows to policy work

Legora’s [BAR description](https://legora.com/bar) motivates evaluating a complete work product in its actual source environment, with explicit rubrics and costs. Its [editor documentation](https://legora.com/product/editor) also makes source-linked drafting concrete. These are product references, not partners, dependencies or proof of comparable capability.

For TACITUS, the practical unit is a policy task, a dated source collection, a semantic layer, a bounded context capsule and a cited draft that a reviewer can inspect. The current observed case is a historical Syria negotiation-policy note. It is a smoke test, not a domain-expert benchmark.

## Open research questions

- Does structured context reduce attribution, identity, scope and modality errors on held-out policy tasks?
- When does preparation and context overhead outweigh reuse benefits?
- Can a retrieved diplomatic formulation retain its speaker, conditions and permitted use?
- Which graph retrieval method improves a specific question, rather than merely making a larger graph?
- How should an expert record a correction without erasing the source claim or earlier interpretation?

Store new ideas as authored notes with source links, a concrete test and a stated implementation status. Keep private work and restricted documents out of this public index.

## Wind Tunnel US benchmark

Reproduce the institutional-confidence comparison between two GSS waves and two Vertex pretest methods. [Benchmark and scoring code](wind-tunnel-us/v1/)
