# A reference changed. The guidance didn’t.

The April 2024 draft of NIST’s Generative AI Profile lists its source-and-citation verification advice as **MS-2.5-008**. The July final lists the same wording as **MS-2.5-003**. The draft’s **MS-2.5-003** concerns a different practice. Looking up the identifier without an edition pin would attach the wrong evidence to the release decision. [April table, printed p. 39](https://airc.nist.gov/docs/NIST.AI.600-1.GenAI-Profile.ipd.pdf#page=44) · [July table, printed p. 31](https://nvlpubs.nist.gov/nistpubs/AI/NIST.AI.600-1.pdf#page=35)

The proposed decision keeps citation verification during pre-deployment measurement and ongoing monitoring, and changes the citation to the final action. The source provides suggested guidance, and the decision is an authored proposal. The reference tool records no human approval and calls no model.

## Reproduce the proof

Run from `reference-pipeline` with Python 3.11 or newer.

```sh
PYTHONPATH=src python examples/citation-guidance/compile.py --output build/citation-guidance
cmp examples/citation-guidance/proof.json build/citation-guidance/proof.json
diff -r examples/citation-guidance/compiled build/citation-guidance/compiled
```

[Proof](proof.json) contains exact offsets into both source excerpts, their SHA-256 pins, the proposed decision and the assembly receipt. [Previously pinned sources](capture.json) describes the official PDF bytes and extraction. The compiler validates type and relation rules, uses an explicit selection layer to carry all three relevant passages as a bounded capsule, and emits a [graph](compiled/graph.json), [JSON-LD graph](compiled/graph.jsonld), [capsule](compiled/capsule.json) and [review sheet](compiled/brief.md). The JSON-LD file uses the reference graph’s application vocabulary.

## Validate the standards export

The companion [standards JSON-LD](compiled/standards.jsonld) describes review practices as SKOS concepts and binds each authored statement to its exact span and source edition with PROV-O. The [SHACL shapes](shapes.ttl) check that lineage and preserve the proposed review status and suggested-guidance modality. Run the optional verifier with the pinned validation dependencies. It also checks that dropping provenance or changing the modality to an obligation fails validation.

```sh
python -m pip install pyshacl==0.40.2 rdflib==7.6.0
python examples/citation-guidance/verify-standards.py build/citation-guidance/compiled/standards.jsonld
```

## Verify the official-source capture

Download the official PDFs as `draft.pdf` and `final.pdf` into a local directory. Run the same command with `--verify-pdfs /path/to/downloads` and a fresh output path. The script verifies PDF SHA-256 first, extracts the pinned page with Poppler `pdftotext -layout`, takes the action ID and action text columns, joins wrapped lines, normalizes typographic ligatures, and checks the exact excerpt bytes. Poppler 25.03.0 was used to reproduce both captures. Source locators use Unicode code points in the normalized UTF-8 excerpts. The corresponding official PDF page and printed page are both recorded.

Review the source rights in the capture manifest. The excerpts retain attribution to NIST and reproduce selected US government text. [NIST publication rights](https://www.nist.gov/nist-research-library/nist-publications) · [NIST public library FAQ](https://www.nist.gov/nist-research-library/library-faqs)
