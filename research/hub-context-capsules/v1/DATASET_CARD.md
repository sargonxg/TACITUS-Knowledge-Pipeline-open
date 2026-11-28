---
pretty_name: TACITUS Context Capsules
language: en
license: other
license_name: original-eu-source-terms
license_link: RIGHTS.md
size_categories:
- 1K<n<10K
task_categories:
- other
tags:
- knowledge-graph
- context-engineering
- provenance
- policy-research
- retrieval
configs:
- config_name: records
  data_files:
  - split: data
    path: records.jsonl
- config_name: relations
  data_files:
  - split: data
    path: relations.jsonl
- config_name: capsules
  data_files:
  - split: data
    path: capsules.jsonl
---

# TACITUS Context Capsules

<img src="https://tacitus.me/assets/brand/tacitus-guide.v1.webp" width="58" alt="The TACITUS pixel guide" align="right">

[GitHub implementation](https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open) · [Hugging Face profile](https://huggingface.co/Giuliocc) · [Interactive source map](https://tacitus.me/structures/?view=all#source-map) · [Sign in to TACITUS App](https://app.tacitus.me/)

**4,808 exact source records, 7,427 typed links and seven bounded context capsules.** This public research release lets a reader inspect the evidence, editions and qualifications selected for a question. It contains no customer conversations, model answers or new human approvals. The working product remains behind authentication.

## Inspect the context behind a question

Browse **records** for original passages and their source offsets. Browse **relations** for containment, explicit references and literal terminology links. The **capsules** table lists seven authored reading questions; open its `path` for the complete JSON packet, including source pins, qualifications, open questions and a byte budget.

Examples include the condition that a receiving third party **draws strongly** on a credit score in C-634/21; the **where designated** qualifier in GDPR Article 35(2); and the distinction between competition-authority GDPR review and consent validity in C-252/21. Read the quoted editions and task boundaries before drawing a conclusion.

The large source collection supports selecting a smaller context for a task. Its size is not a quality score. These capsules are published research objects, not a substitute for a team's own decisions and source review. No model is trained by this release, and no improvement in answer quality, hallucination rate or total cost is established by publishing the graph.

## Verify offline

Download this repository at an immutable commit or release tag, then run:

```sh
python verify.py
```

The standard-library verifier checks file hashes, exact Unicode quotation offsets, source editions, graph endpoints, viewer rows, capsule checksums, budget bounds and the explicit `not_expert_approved` status. It makes no network or model calls. The [original source extractor and verifier](https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open/tree/b96550da802c2992577142016245c6453d937e8b/research/ai-governance-source-map/v2) additionally reproduce extraction from the raw official snapshots. [Capsule compiler and qualification checks](https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open/tree/c18dc4e84d77fea4699365184a3c0784cda21ad8/research/ai-governance-source-map/context-packets-v1)

## Use with the App

TACITUS App lets a team attach its sources, capsules and artefacts to conversations and hand over the selected context. This research graph is not automatically attached to any account or model. Its reading packets are separate from the App's import format. To build your own App-importable package, use the public [reference pipeline and import contract](https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open/tree/main/reference-pipeline).

## Sources and limits

Four adopted EU instruments and three historical CJEU judgments retain their official URLs, dates, editions and hashes. They are frozen English-language snapshots, not current consolidated law. The judgments are translations. Reading routes are TACITUS-authored guidance; they do not establish applicability or legal-expert approval. Lexical references and defined-term mentions are incomplete and do not establish entailment or synonymy.

Original source terms, attribution and qualifications remain in [RIGHTS.md](RIGHTS.md) and the source metadata. The official texts are not relicensed under the software's license. Keep these terms and limitations with reused material. There are no train/test efficacy labels or independent human annotations in this dataset. An evaluation of generation quality needs matched questions, baselines, full costs and domain review.
