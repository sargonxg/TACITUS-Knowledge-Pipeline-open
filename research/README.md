# Research behind the policy-data workflow

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
