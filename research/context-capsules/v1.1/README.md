# TACITUS research proposal · version 1.1

**TAC-2026-01 · 24 November 2026. Research proposal, not independently peer-reviewed.** Efficacy studies are proposed, not preregistered or run. This release revises the argument and experimental design; it reports no new model inference.

The paper proposes a portable context contract for conversation and writing: exact evidence, explicit interpretations and qualifications, scoped review, generation selection and reusable work products. It describes the implemented reference algorithm and a real NIST draft-to-final source-edition example. It then proposes comparisons with strong hybrid retrieval/reranking, full documents with a careful working note, and an equivalent-information flat packet. Annotation, review and maintenance costs are included.

- [Read the manuscript](paper.md)
- [Download the paper](tacitus-context-capsules-v1.1.pdf)
- [Read the accessible HTML](https://tacitus.me/research/context-capsules/paper/v1.1/)
- [BibTeX](citation.bib) · [21 references](references.json) · [literature map](literature-map.json)
- [Real source-edition case](source-edition-case.json) · [evaluation proposal](evaluation-protocol.json)
- [Implementation boundaries](implementation-status.json) · [revision critique](REVIEW_NOTES.md)
- [Manifest and checksums](manifest.json)
- [Archived version 1.0](../v1/README.md)

## Reproduce

From the repository root, Python 3.11 or later suffices for the replay and verification:

```sh
python research/context-capsules/v1.1/replay.py
python research/context-capsules/v1.1/verify.py
```

The replay checks exact captured NIST text, source versions and spans, rebuilds the 4,726-byte source-edition packet and independently checks the six historical provider-record receipts. It does not download documents, contact a model or test the production App route. Source PDF hashes, page locators and extraction rules live in `reference-pipeline/examples/citation-guidance/`; optional PDF verification is documented there.

To regenerate the PDF, semantic HTML, vector figures and checksum manifest, also install Matplotlib, Pandoc with citeproc, XeLaTeX and the fonts identified in `build.py`, then run:

```sh
python research/context-capsules/v1.1/build.py
python research/context-capsules/v1.1/verify.py
```

The manifest pins public reference commit `9fa96f66593902c5631efc391ef449a9c724b958`, exact relevant reference-file hashes and the prior private App source-review commit. The private application is not reproduced here; documented hosted generation remains paused. PDF byte identity can depend on toolchain versions; the included manifest describes this released artifact, and the replay checks deterministic data identity.

The earlier synthetic renewal fixture and six November 23 provider probes remain development compatibility records. They are not a held-out benchmark and showed mixed effects. Neither this source-edition example nor those probes establish generation quality, productivity or customer value.

## Citation

TACITUS. (2026). *TACITUS: Context Capsules, Artefacts, and Small Knowledge Graphs for AI Generation* (Research proposal TAC-2026-01, version 1.1). <https://tacitus.me/research/context-capsules/paper/v1.1/>

No DOI or independent peer review is claimed. Source materials retain their respective rights and attribution. TACITUS is the institutional author and has a commercial interest in the system. AI assistance is disclosed in the paper.
