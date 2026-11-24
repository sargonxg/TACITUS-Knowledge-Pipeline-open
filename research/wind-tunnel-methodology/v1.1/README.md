# Wind Tunnel methodology · Working paper WT-2026-01

**TACITUS (2026). _Wind Tunnel: Evidence-Separated Population Modeling for AI-Assisted Research Preparation._ Version 1.1, 24 November 2026.** Institutional working paper; independent peer review has not been completed.

[Read version 1.1](https://tacitus.me/research/wind-tunnel/paper/v1.1/) · [Download PDF](wind-tunnel-methodology-v1.1.pdf) · [BibTeX](citation.bib) · [Source manuscript](paper.md) · [Revision notes](REVISION_NOTES.md)

Wind Tunnel organizes population definitions, questionnaire versions, model-assisted assumption exploration, and separately identified human evidence. This paper documents its twelve-cell US answer-generation recipe, zero-weight qualitative dossiers, frozen provenance records, and a retrospective comparison on twelve GSS institutional-confidence items. The 2022 human-survey persistence baseline has mean total variation of **2.48 percentage points**, versus **7.50** for a national model call and **8.16** for the conditioned, weighted recipe. These are unchanged descriptive scores, not evidence of representative public-opinion measurement or a universal comparison of human and AI research.

The comparison changes prompting, call structure, and weighting together; it does not isolate a causal weighting effect. The 2024 weighted GSS reference is a survey estimate, not population truth. A separate questionnaire-preparation workflow and its proposed human evaluation are described; their effectiveness has not been measured here. See [the evaluation agenda](evaluation-agenda.json) for the distinction between these research questions.

## Rebuild and verify

From the public repository root:

```sh
node research/wind-tunnel-us/v1/score.mjs verify research/wind-tunnel-us/v1/benchmark.json
python research/wind-tunnel-methodology/v1.1/build.py
python research/wind-tunnel-methodology/v1.1/verify.py
```

Requires Node.js 20 or later; Python 3 with Matplotlib; Pandoc with citeproc; and XeLaTeX with Latin Modern fonts. The unchanged sibling `research/wind-tunnel-us/v1/benchmark.json` contains aggregates, not individual respondent data. Building uses no network request or model call.

`paper.md` is the authored manuscript with table slots. `manuscript.md` contains the recomputed tables. `references.json` is CSL bibliography data. `header.tex` and `latex-layout.lua` control PDF typography; the versioned `.tex` is the complete generated source. Vector PDF/SVG figures share the same released data. `index.html` is a script-free reading page with native MathML, captioned tables, section anchors, and linked references; `article.html` and `paper.json` are integration inputs. `manifest.json` records the benchmark identity and publication artifact hashes. It excludes itself to avoid a self-referential hash.

The verifier checks all manifest hashes, the original benchmark scorer, unchanged v1 results, citation coverage, version/canonical metadata, accessible table captions, MathML equations, unique anchors, internal links, and compatibility with a strict content-security policy. It does not validate human responses or private implementation claims.

## Reproducibility and version history

Benchmark/scorer source: commit `2b51dfee375b1ee0e5fd1ee7a99edd1623d8cac4`. Application implementation described: version 3.12.1, commit `546b24d1f47671ff917ac1a09eb3bc5d9ab54d15`. Public score replay is possible; private generation templates and complete input construction are not released. A run hash identifies a record, not independent reconstruction or target concealment.

[Version 1.0 remains available](https://tacitus.me/research/wind-tunnel/paper/) with its original source directory. This revision changes exposition, figures, and evaluation design; it does not replace the benchmark or make a new inference call. Preserve each substantive publication revision and its citation URL.

The original manuscript and figures follow the repository license. GSS, ACS, and other source materials retain their own terms. Institutional authorship and citations imply no journal acceptance, independent review, or source-organization endorsement.
