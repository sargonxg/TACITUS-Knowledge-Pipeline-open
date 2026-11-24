# TACITUS context capsules: research proposal

**TAC-2026-01 · version 1.0 · 23 November 2026. Not independently peer-reviewed.**

*TACITUS: Context Capsules, Artefacts, and Small Knowledge Graphs for AI Generation.* An architecture and evaluation proposal for the conversation and writing workspace at [app.tacitus.me](https://app.tacitus.me/).

[Typeset paper](tacitus-context-capsules-v1.0.pdf) · [Manuscript](paper.md) · [Bibliography](references.json) · [Proposed evaluation](evaluation-protocol.json) · [Implementation status](implementation-status.json) · [BibTeX](citation.bib)

The proposal describes reusable context, exact sources, qualifications, prior discussion, explicit analytical warrants, bounded graph selection, artefacts, and human/agent handover. Its controlled generation and team studies are **proposed, not registered or completed**. Earlier six-response provider observations are mixed and are not a general accuracy benchmark. Hosted App generation remains gated in the documented release.

## Reproduce without a model

From the repository root:

```sh
git checkout tacitus-context-capsules-v1.0
python research/context-capsules/v1/replay.py
```

The release tag retains the exact reference code and historical receipts used by this proposal. Use that tag when later pipeline development changes the working branch.

The replay validates three original synthetic sources, four proposed mappings and their exact qualifications, a bounded capsule, an App import bundle, and the hashes of six historical provider recordings. It verifies refusal when mandatory complete context cannot fit. It performs zero model calls and uses no network or credentials. The demonstration does not represent an actual meeting, real licence decision, or human-approved interpretation.

`demo/app-bundle.json` can be previewed in the authenticated App's **Library → Import context graph**. It is an illustrative proposed package; importing is distinct from human acceptance or generation. The public paper does not grant workspace access or claim new hosted dispatch acceptance.

## Build and verify the publication

Requires Python 3 with Matplotlib, Pandoc with citeproc, and XeLaTeX with Latin Modern fonts:

```sh
python research/context-capsules/v1/build.py
python research/context-capsules/v1/verify.py
```

The builder creates an academic PDF, TeX, accessible HTML with native MathML, eighteen references, two original vector figures, and an artifact manifest. `verify.py` checks all hashes, citation and section links, tables and equations, proposal status, source pins, and replayed context. A checksum establishes byte identity, not empirical truth, reviewer identity, or provider authenticity.

The existing Wind Tunnel publication and its frozen version are separate and unchanged. The code and original authored material follow this repository's Apache-2.0 license; cited publications retain their original rights. TACITUS is both the developer and publisher. AI assistance is disclosed; independent expert review has not occurred.
