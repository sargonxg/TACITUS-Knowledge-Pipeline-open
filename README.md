# TACITUS Knowledge Pipeline

<img src="docs/brand/tacitus-guide.v1.webp" width="59" height="88" align="right" alt="The TACITUS guide for reusable source-linked context">

TACITUS experiments with infrastructure for better AI knowledge generation. Build reusable, source-linked context for a team: exact passages, authored interpretations, qualifications and work products, selected into a bounded capsule for a task. The goal is to keep the context a teammate or agent needs when work continues.

[Company](https://tacitus.me/) · [App](https://app.tacitus.me/) · [Organization](https://github.com/TACITUS-me) · [Reference implementation](reference-pipeline/)

## Current research releases

- **[TACITUS context capsules · v1.1](research/context-capsules/v1.1/README.md)** — [PDF](research/context-capsules/v1.1/tacitus-context-capsules-v1.1.pdf) · [read online](https://tacitus.me/research/context-capsules/paper/v1.1/). A source-backed architecture and controlled evaluation proposal, including a real NIST draft-to-final handover case and 21 references. Confirmatory efficacy studies have not been run.
- **[Wind Tunnel methodology · v1.1](research/wind-tunnel-methodology/v1.1/README.md)** — [PDF](research/wind-tunnel-methodology/v1.1/wind-tunnel-methodology-v1.1.pdf) · [read online](https://tacitus.me/research/wind-tunnel/paper/v1.1/). An experimental research-preparation procedure and a replayable retrospective GSS comparison. On the twelve selected items, the conditioned recipe has no mean advantage over a national model call.
- **[AI governance source map · v1](research/ai-governance-source-map/v1/README.md)** — **2,793 source-linked records and 4,517 typed links**, derived from pinned official AI Act and GDPR adopted texts. Exact quotations, source editions, structural links, lexical references and document-specific definitions are inspectable and rebuilt offline.

The papers are institutional working research, not independently peer-reviewed. [The research index](research/README.md) separates implemented checks, recorded results and proposed studies. Both original v1.0 papers remain unchanged in their archived directories. The source map is a document graph of adopted editions, not a current consolidated legal analysis or a generation-quality benchmark; a task capsule selects a smaller subgraph for the actual question.

## Build and import a context graph

Python 3.11+. The reference path uses the standard library and makes zero model calls.

```sh
git clone https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open.git
cd TACITUS-Knowledge-Pipeline-open/reference-pipeline
PYTHONPATH=src python -m tacitus_pipeline build \
  --input examples/team-handoff/collection.json \
  --ontology ontology/team-knowledge.json \
  --layer layers/team-handoff.json \
  --question "What context should travel with a team handoff?" \
  --app-export --output build/team-handoff
```

Open the App Library, select **Saved capsules → Import context graph**, and upload `build/team-handoff/app-bundle.json`. Preview the passages and qualifications before saving the sources, capsule and artefact. Review the proposed graph before activating it. The demonstration discussion is an authored fixture.

## What the implementation does

- Verifies source editions, Unicode quotation spans, ontology domain/range and required qualifications.
- Builds graph JSON, JSON-LD, a bounded context capsule, an evidence worksheet and a checksum receipt.
- Supports explicit selection, BM25 passage matching and graph expansion bounded to two hops. The selection report explains included and omitted records.
- Compares source collections and identifies interpretations affected by changed editions.
- Exports `tacitus-pipeline-import/1` for the App. Native App records have their own versions and review history.
- Writes a complete output directory with rollback if the final directory replacement fails.

The App preview checks exact text and maps Python code-point offsets to UTF-16 offsets. Importing context makes no model call. Hosted App generation is paused.

## Connect a local model to the App

The [local companion](local-companion/) pairs an Ollama or LM Studio server with one authenticated App workspace. Choose an installed model in Conversation or Writing; the companion receives a bounded request, calls your configured loopback server and returns a validated result. Pairing and discovery make no inference calls. The companion downloads no model weights, exposes no public inference endpoint and never automatically repeats an uncertain generation attempt. Generation follows the App's workspace control and remains paused in the hosted release.

Node 24+, with no package dependencies. [Setup, data boundaries and testing limits](local-companion/README.md).

## Verify

```sh
cd reference-pipeline
PYTHONPATH=src python -m unittest discover -s tests -v
python benchmarks/run.py
```

[Format and import guide](reference-pipeline/docs/app-import.md) · [Ontology](reference-pipeline/docs/ontology.md) · [Task layers](reference-pipeline/docs/semantic-layers.md) · [Model evaluation protocol](reference-pipeline/benchmarks/model-evaluation-plan.json)

The assembly measurements concern retained evidence, selection and byte budgets. The earlier model comparison was mixed. A new quality or workflow-efficiency result requires matched model runs and human review.

## Research and earlier experiments

[Research index](research/README.md) maps primary papers to engineering questions. The original notebooks and provider experiments remain available with their separate dependencies. The maintained starting point is `reference-pipeline/`.

Original code is Apache-2.0. Source documents retain their original attribution and terms.

## Recorded provider compatibility check

[Six live synthetic Cloudflare requests and their failures](reference-pipeline/evaluations/2026-11-23-provider-probe) retain exact inputs, final answers, model identities and token usage. All six responses satisfy the requested JSON schema and resolve their citation IDs. Gemma’s flat answer omits a required condition; GLM’s graph-assisted answer strengthens the procedural status. One task is not a quality benchmark or App/Gateway acceptance. No new inference is needed to inspect these records.


## Verify research releases

Python 3.11+ and Node.js 20+ are sufficient to verify the released artifacts, source spans, graph extraction and score replay. No model calls, credentials, package installation or PDF build tools are required for these checks.

```sh
python research/context-capsules/v1/verify.py
python research/context-capsules/v1.1/verify.py
python research/wind-tunnel-methodology/v1/verify.py
python research/wind-tunnel-methodology/v1.1/verify.py
python research/ai-governance-source-map/v1/verify.py
```

[CI](.github/workflows/context-proposal.yml) runs these checks for research changes. The paper manifests preserve publication hashes and source identities. The source-map verifier rebuilds every record and link from pinned XHTML and checks exact text offsets, relation constraints, counts and cross-instrument reference regressions. Rebuilding typeset PDFs requires the optional toolchain documented with each paper.
