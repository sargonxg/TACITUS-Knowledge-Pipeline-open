# TACITUS Knowledge Pipeline

Build reusable, source-linked context for a team. The pipeline connects exact passages, authored interpretations and qualifications, then selects a bounded capsule for a task.

[Company](https://tacitus.me/) · [App](https://app.tacitus.me/) · [Organization](https://github.com/TACITUS-me) · [Reference implementation](reference-pipeline/)

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
