<img src="assets/images/tacitus-logo.png" alt="TACITUS" width="130"/>

# TACITUS Knowledge Pipeline

[TACITUS](https://app.tacitus.me/) is a conversation workspace for teams. Save the instructions, sources and examples that made one conversation useful. Attach them when you start the next one or hand the work to a teammate.

[Open the App](https://app.tacitus.me/) · [Try a conversation](https://app.tacitus.me/try.html) · [TACITUS website](https://tacitus.me/) · [App availability](https://app.tacitus.me/api/health)

This repository contains the public reference compiler. It shows how exact source passages, authored mappings and review rules become a bounded context package and an inspectable review sheet.

| Piece | What it carries |
| --- | --- |
| **Capsule** | Background, working instructions, selected evidence and checks to apply again. |
| **Artefact** | A template, example or deliverable that shows what useful work should look like. |
| **Knowledge graph** | Typed links between source editions, exact passages, statements and qualifications. |
| **Semantic layer** | The parts of the graph and the review rules relevant to one task. |

## Run the exact-source compiler

Use Python 3.11 or newer. The pinned example can be rebuilt locally with the standard library. It uses recorded public excerpts and makes zero model calls.

The April 2024 draft of the NIST Generative AI Profile called its citation-checking guidance `MS-2.5-008`. The July final uses `MS-2.5-003` for the same wording. That identifier meant something different in the draft. The proof preserves the wording and proposes a citation update.

```sh
git clone https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open.git
cd TACITUS-Knowledge-Pipeline-open
git checkout --detach be8640a6a2b5ff2755c884e9e7eae981bb98e62e
cd reference-pipeline
PYTHONPATH=src python3 examples/citation-guidance/compile.py --output build/citation-guidance
cmp examples/citation-guidance/proof.json build/citation-guidance/proof.json
diff -r examples/citation-guidance/compiled build/citation-guidance/compiled
```

Open `build/citation-guidance/proof.json` for the proposed judgment, then `build/citation-guidance/compiled/brief.md` for its supporting passages and reviewer checks. The other outputs show how the compiler assembled the context.

- `graph.json` and `graph.jsonld` record exact source links, statement types and qualifications.
- `capsule.json` packages the selected evidence and task checks within an explicit byte budget.
- `standards.jsonld` maps provenance and named concepts to PROV-O and SKOS. The optional SHACL verifier checks the export structure.
- `receipt.json` records what was selected, the size and content hash of the result, and the number of model calls.
- `workflow.json` describes a read-only workflow plan.

[Inspect the pinned source capture, outputs and validation steps](https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open/tree/be8640a6a2b5ff2755c884e9e7eae981bb98e62e/reference-pipeline/examples/citation-guidance) · [April NIST draft](https://airc.nist.gov/docs/NIST.AI.600-1.GenAI-Profile.ipd.pdf#page=44) · [July NIST final](https://nvlpubs.nist.gov/nistpubs/AI/NIST.AI.600-1.pdf#page=35)

## Inspect and verify the code

From `reference-pipeline`:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 benchmarks/run.py
```

The tests check source versions, exact offsets, preserved qualifications, type and relation rules, and context limits. The example’s citations are inspectable and its mappings remain proposed. A reviewer still decides whether the passages support the judgment. The assembly benchmarks measure evidence retention and packet size. Evaluation of answer quality and analyst time is pending.

[Source capture](reference-pipeline/docs/sources.md) · [Ontology](reference-pipeline/docs/ontology.md) · [Semantic layers](reference-pipeline/docs/semantic-layers.md) · [Benchmark method](reference-pipeline/docs/benchmarking.md) · [Model evaluation plan at the example pin](https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open/blob/be8640a6a2b5ff2755c884e9e7eae981bb98e62e/reference-pipeline/benchmarks/model-evaluation-plan.json)

## Working boundaries

The hosted App is experimental. The public practice prepares local request previews and template-based outlines. Check App availability for hosted generation. The public compiler uses its own reference format. The App and Workbench have separate versioned formats and access rules. Optional model adapters and their saved outputs are documented as separate experiments.

[App availability](https://app.tacitus.me/api/health) · [Format compatibility](https://github.com/sargonxg/tacitus-workbench/blob/main/docs/FORMAT_COMPATIBILITY.md) · [Earlier model experiments](reference-pipeline/docs/model-workflows.md) · [Research index](research/README.md) · [Guide and teaching demo](TACITUS_GUIDE.md)

<details>
<summary>Earlier examples, tools and research</summary>

- [Assessment example](reference-pipeline/examples/assessment), [historical agent recording](reference-pipeline/examples/syria-negotiation/agent-step-2) and [source-linked language review](reference-pipeline/docs/diplomatic-language.md).
- [Earlier notebooks and service dependencies](docs/legacy-notebook-readme.md), [research and design notes](https://github.com/sargonxg/sargonxg/blob/main/docs/RESEARCH_AND_DESIGN.md) and [TACITUS public project map](https://github.com/sargonxg/sargonxg/blob/main/docs/PUBLIC_PROJECT_MAP.md).

</details>

The code uses the [Apache-2.0 license](LICENSE). Public source materials retain their attribution and terms. Report security issues using [SECURITY.md](SECURITY.md).
