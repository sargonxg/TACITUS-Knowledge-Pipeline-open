# Wind Tunnel methodology · Working paper WT-2026-01

**TACITUS (2026). _Wind Tunnel: Evidence-Separated Population Modeling and AI-Assisted Questionnaire Pretesting._ Version 1.0, 23 November 2026.** Institutional working paper; not independently peer-reviewed.

[Read the published paper](https://tacitus.me/research/wind-tunnel/paper/) · [Download PDF](wind-tunnel-methodology-v1.0.pdf) · [BibTeX](citation.bib) · [Source manuscript](paper.md)

The paper describes the evidence model, twelve-cell US pretest, zero-weight qualitative dossiers, provenance records and a retrospective comparison against twelve GSS confidence items. The earlier human survey outperforms both model methods on mean total variation and Brier score. This result does not validate the legacy scenario indicators or establish representative public opinion.

## Rebuild

Requires Python 3 with Matplotlib, Pandoc with citeproc, XeLaTeX with Latin Modern fonts, and the unchanged `research/wind-tunnel-us/v1/benchmark.json` in this repository. The supplied aggregates contain no respondent microdata. The builder makes no network request or AI call.

```sh
node research/wind-tunnel-us/v1/score.mjs verify research/wind-tunnel-us/v1/benchmark.json
python research/wind-tunnel-methodology/v1/build.py
python research/wind-tunnel-methodology/v1/verify.py
```

`paper.md` is the authored manuscript with table slots. `manuscript.md` includes recomputed tables. `references.json` is CSL bibliography data. `header.tex` supplies the PDF typography; `wind-tunnel-methodology-v1.0.tex` is the complete generated TeX. Vector PDF/SVG figures share the same computed data. `index.html` is the standalone reading page; `article.html` and `paper.json` are server-rendered application inputs. `manifest.json` records artifact hashes, publication version and benchmark identity.

Canonical benchmark source commit: `2b51dfee375b1ee0e5fd1ee7a99edd1623d8cac4`. Application implementation reviewed: version 3.12.1, commit `546b24d1f47671ff917ac1a09eb3bc5d9ab54d15`. Score replay is public; the private prompt templates, workbook mapping and complete generation pipeline are not released. The paper expressly distinguishes those levels of reproducibility.

## Versioning and source rights

Publish substantive changes as another version and retain the original release. Manuscript and original figures follow the repository license. GSS, Census and other referenced materials retain their own source terms. Citation links and institutional authorship do not imply endorsement, journal acceptance or external review.
