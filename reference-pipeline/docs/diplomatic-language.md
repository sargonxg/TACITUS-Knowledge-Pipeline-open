# Diplomatic language review: a runnable public reference

Keep an exact source passage, a declared wording choice, proposed drafts and their discussion linked together. This tool uses the existing source → graph → capsule compiler. It adds no model dependency or private app code.

## Build from a clean checkout

Python 3.11+, standard library only. No package installation, account, provider key or paid inference:

```sh
git clone https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open.git
cd TACITUS-Knowledge-Pipeline-open/reference-pipeline
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m tacitus_pipeline.language \
  --input examples/syria-negotiation/collection.json \
  --ontology ontology/negotiation.json \
  --layer layers/syria-negotiation.json \
  --history examples/syria-negotiation/language-history.json \
  --output build/language-review
```

Inspect `build/language-review/language-review.json` and `language-graph.json`. Existing outputs require another directory or explicit `--force`. The committed [review packet](../examples/syria-negotiation/language-review/language-review.json) is reproducible from those public inputs.

## One realistic review problem

Paragraph 4 of UN Security Council resolution 2254 (2015) “Expresses its support” for a political process, includes “within a target of six months”, and qualifies election language with “pursuant to the new constitution”. A deliberately problematic **human-authored synthetic** draft says governance was established and elections guaranteed. A second synthetic draft quotes the support language and conditions. These are editorial exercises, not actual diplomatic negotiations, present-day findings, expert-approved interpretations or model generations.

The tool records three literal checks for this draft: the two declared qualifications and one source-backed wording choice. The first draft repeats none; the second repeats all three. This is a structural retention example, not a semantic-quality benchmark. A paraphrase may be appropriate, and an exact phrase can still accompany a false claim.

## What is preserved

- Full normalized public source snapshot, URL, rights note and SHA-256 version; exact source/evidence offsets use Unicode code points.
- Existing typed statements, proposed interpretations, entities, conditions and semantic-layer checks.
- A declared language choice and authored rationale linked to its actual source wording.
- Two draft versions with a revision edge, explicit citations and content digests.
- Five clearly synthetic proposal/discussion/pending-review events, ordered with a local hash chain.
- A 23-object, 34-relationship graph connecting source, evidence, wording, drafts and history. Counts describe this example, not a corpus of political facts.

The compiler refuses changed source bytes, unquoted wording choices, unknown/duplicate citations, revision cycles, discussion before proposal, unresolved discussion references and injected approval fields. It does not infer legal effect, certify truth, verify authors or authorize actions. A hash chain checks internal consistency; it cannot prove that the entire file was not rewritten.

## Use the same packet in the public workbench

Open [the language desk](https://tacitus.me/workbench/#language), or build the [existing Workbench](https://github.com/sargonxg/tacitus-workbench/blob/main/apps/workbench/docs/diplomatic-language.md). Compare versions, inspect evidence and graph objects, add a local proposal or discussion note, and export the review record. The browser validates the source snapshots, capsule, derived graphs, digests, ordering and literal findings. No model call or server write occurs. Local edits disappear on reload unless exported.

`tacitus-language-history/1` is the compiler's bounded seed history. `tacitus-language-review/1` is the assembled browser review packet; import/export it through the language desk. Neither is a native PRAXIS or private app import contract. The existing recorded model workflow remains a separate tool and example.

## Public demo and private product

This Apache-2.0 reference implementation uses existing public official source material, attributed normalized excerpts and explicitly synthetic editorial drafts/comments. Source conditions remain separate from code licensing. The Workbench's own modules retain their existing reserved-rights notices; public visibility is not an open-source license grant.

The private app, proprietary assets, user records, credentials and private evaluation sets are not included. This example does not establish production agent orchestration, authenticated collaboration, live drafting, legal review or better generation quality. Those require separate implementation and acceptance.
