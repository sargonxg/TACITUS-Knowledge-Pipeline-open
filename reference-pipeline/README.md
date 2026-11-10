# TACITUS knowledge pipeline

Build a source-linked policy graph, apply an explicit semantic layer and prepare bounded context for a reviewable artifact.

**Start here:** the credential-free Python reference below. It works from exact source text and authored annotations. It does not extract meaning automatically, call a model, approve an interpretation or execute external actions.

[Website](https://tacitus.me/) · [TACITUS organization](https://github.com/TACITUS-me) · [LinkedIn](https://www.linkedin.com/company/tacitus-me) · [Benchmark plan](benchmarks/model-evaluation-plan.json)

## Run a useful example

Python 3.11+. No dependencies, credentials, database service or model provider required.

```sh
git clone https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open.git
cd TACITUS-Knowledge-Pipeline-open/reference-pipeline
PYTHONPATH=src python -m tacitus_pipeline build \
  --input examples/assessment/collection.json \
  --ontology ontology/policy.json \
  --layer layers/assessment-evidence.json \
  --question "Map assessment evidence and review roles." \
  --output build/assessment
```

The example maps original adopted EU AI Act/GDPR passages to a specific assessment-coordination question. It preserves the conditional FRIA/DPIA relationship, the DPO designation condition and the separate AI Office template role. The mappings are authored proposals. Current legal status, applicability and the actual system need separate review.

Inspect `build/assessment/brief.md`, then `capsule.json` and its receipt. Existing output files require an explicit `--force` to overwrite. Optional editable installation: `python -m pip install -e .`; this project is not claimed to be published on PyPI.

## What the code builds

| Output | What it contains |
| --- | --- |
| `graph.json` | Typed entities, reified proposed statements, exact evidence spans, qualifications and source editions for the complete selected layer. |
| `graph.jsonld` | The same application records and relationships as JSON-LD. |
| `capsule.json` | Whole required statements, source references, review checks and explicit omissions inside a UTF-8 byte budget. |
| `brief.md` | A populated evidence-review sheet with quotes and reviewer checks, not a generated legal opinion. |
| `workflow.json` | A bounded read-only workflow plan; it is not agent execution or a PRAXIS import contract. |
| `receipt.json` | Context checksum, byte count, selection counts and zero model calls. |

The full layer graph and bounded capsule are different outputs. The graph may contain statements omitted from the capsule. Do not substitute the graph for a bounded model input.

## Build your own structure

- [Sources and evidence](docs/sources.md): pin exact UTF-8 text, source edition, scope and rights notes.
- [Ontology](docs/ontology.md): define entity types and relation domain/range; keep proposed claims separate from facts.
- [Semantic layers](docs/semantic-layers.md): select statements and required qualifications for one analytical job.
- [Workflow](docs/workflows.md): verify, validate, select, render and review before any external action.
- [Benchmarking](docs/benchmarking.md): run assembly diagnostics and inspect the model-evaluation work still required.

Source: [`core.py`](src/tacitus_pipeline/core.py). Example data: [`collection.json`](examples/assessment/collection.json). Ontology: [`policy.json`](ontology/policy.json). Semantic layer: [`assessment-evidence.json`](layers/assessment-evidence.json).

## Verify

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
python benchmarks/run.py
```

Tests cover source and span tampering, lost declared qualifiers, stale versions, invalid relation types, missing references, review-state promotion, duplicate editions, byte limits, Unicode offsets and overwrite refusal. GitHub Actions runs the same credential-free path.

Assembly measurements are not proof of better AI generation. The [model-output benchmark plan](benchmarks/model-evaluation-plan.json) is explicitly **work in progress**. A pilot needs held-out tasks, matched source pools, recorded model usage and domain review.

## Other TACITUS work

[Context workbench](https://github.com/sargonxg/tacitus-workbench) · [DIALECTICA capsule core](https://github.com/sargonxg/A3_DIALECTICAbyTACITUS_v3) · [KAIROS temporal engine](https://github.com/sargonxg/KAIROS-temporal-vision-TACITUS) · [TCGC alpha benchmark](https://github.com/sargonxg/TCGC_TACITUS-Conflict-Grammar-Corpus_BENCHMARK).

These repositories have separate contracts and licenses. Their historical test reports are not new verification of every component by this reference tool. PRAXIS is invitation-only and AI generation is currently paused: [open the workspace](https://praxis.tacitus.me/).

## License and source rights

Code retains this repository's Apache-2.0 license. Source documents and referenced projects retain their original attribution and terms; inclusion does not relicense them. See the fixture's rights notes. No new blanket license is granted over third-party data.
