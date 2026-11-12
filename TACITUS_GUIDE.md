# TACITUS-Knowledge-Pipeline-open · purpose and practical use

Compile exact source passages and authored annotations into a bounded policy context, a review worksheet and an inspectable artifact.

**Role:** Local reference implementation.

**Current boundary:** The credential-free compiler and optional model adapters are separate workflows. Cross-repository capsule formats are not interchangeable.

## Start with one useful workflow

Python 3.11+; standard library; no runtime account.

```sh
cd reference-pipeline
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m tacitus_pipeline build --input examples/assessment/collection.json --ontology ontology/policy.json --layer layers/assessment-evidence.json --question "Map assessment evidence and review roles." --output build/portfolio-example
```

These application commands are separate from the teaching demo below. Check the recorded results before treating a command as verified. A successful bundle build does not establish provider availability, authenticated ownership or a working hosted deployment.

## How the code fits together

| Entry point | What to inspect |
| --- | --- |
| [reference-pipeline/src/tacitus_pipeline/core.py](reference-pipeline/src/tacitus_pipeline/core.py) | Validates source editions and authored annotations, selects required evidence and builds bounded graph/context/artifact outputs. |
| [reference-pipeline/src/tacitus_pipeline/generation.py](reference-pipeline/src/tacitus_pipeline/generation.py) | Checks optional model outputs against supplied evidence identifiers. It does not prove semantic entailment. |
| [reference-pipeline/docs/workflows.md](reference-pipeline/docs/workflows.md) | Project-specific contract, implementation status or setup reference. Preserve its stated limits. |

## Its place in TACITUS

The common goal is reusable, reviewable policy context: sources → explicit structure → task context → draft/artifact → human review. This repository contributes the role described above. Existing schemas, identity systems and review receipts remain authoritative within each implementation. A similar name such as “graph”, “context” or “capsule” does not establish binary or semantic compatibility.

For a downstream adapter, first pin a source/version and rights notice, state the task and output schema, retain attribution and time qualifications, then test export/re-import and refusal cases against the actual destination. No adapter is represented as working merely because the two projects appear in this portfolio.

## Play the idea before running the stack

[The House of Evidence](tacitus-demo/index.html) is an original four-room point-and-click adventure. Preserve a conditional promise, attribute a claim, inspect its chronology and download a brief with the uncertainty intact. It is a synthetic teaching fixture, not a run of this repository’s engine.

```sh
python -m http.server 8765 --bind 127.0.0.1 --directory tacitus-demo
```

Open `http://127.0.0.1:8765/`. The directory is also a standalone static artifact: copy its contents to a static host to publish only the adventure. No model, credential, database or package installation is needed. Opening `tacitus-demo/index.html` directly works in browsers that allow local files.

The shared teaching engine passed desktop (1440×1080) and mobile (390×844) Chromium checks for wrong answers, incomplete-review refusal, exact quotation export, separate notes, reset and horizontal overflow. [Fixture receipt](tacitus-demo/browser-verification.json). This verifies the shared demo, not the application.

## Research, credit and the contribution to evaluate

[Lewis et al., RAG (2020)](https://arxiv.org/abs/2005.11401), [Liu et al., Lost in the Middle (2023)](https://arxiv.org/abs/2307.03172), and [Edge et al., GraphRAG (2024; revised 2025)](https://arxiv.org/abs/2404.16130) motivate separating retrieval, context use and global synthesis. Read the [methods, evaluation limits and TACITUS design notes](https://github.com/sargonxg/sargonxg/blob/main/docs/RESEARCH_AND_DESIGN.md). Their results are not measurements of this repository.

Retain existing licenses and notices for application dependencies and bundled sources. The new adventure code, synthetic dispatches and generated mansion artwork are credited in [tacitus-demo/CREDITS.md](tacitus-demo/CREDITS.md). The demonstration does not relicense this repository or its external source documents.

The practical improvement to test is whether this workflow reduces a specific failure or repeated task: lost attribution, omitted conditions, stale evidence, untraceable drafting or repeated source preparation. Measure that against a matched baseline with source review, complete costs and held-out tasks before claiming analytical or efficiency gains.

## Verification in this pass

Audited default-branch baseline: `8eb07355b9ce1cfb9beafeebe49b3e415eb9c5af`. Changes were prepared from a fresh shallow checkout. The audit covers this branch, not every historical or in-progress branch.

| Command | Local result |
| --- | --- |
| `reference-pipeline: python -m unittest discover -s tests -v` | Passed |

A failure is a remaining release blocker for the affected workflow. A passing local test is not a new hosted release. Provider/model quality, current external-service setup and production deployment were not certified.
