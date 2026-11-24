# AI governance source atlas · v2

**4,808 genuine source records, 7,427 typed links, four EU instruments and three historical CJEU judgments.** Every record has an exact quotation, a pinned source edition and Unicode offsets. The full atlas supports inspecting a small selection for an analytical task; its size is not a quality score.

The release retains every v1 record and quotation unchanged, adds the Digital Services Act and Law Enforcement Directive, and gives three real judgments complete numbered-paragraph and operative-part records. Editorial reading routes explain useful questions separately from extracted links. No fictional cases, generated court quotations, approval labels or generation-performance claims are included.

## What a reader can investigate

| Documented event | Source and date | Reading question and boundary |
| --- | --- | --- |
| **SCHUFA scoring · C-634/21** | [CJEU, First Chamber, 7 December 2023](https://juris.curia.europa.eu/juris/document/document.jsf?docid=280426&doclang=EN), ECLI:EU:C:2023:957 | The operative part interprets GDPR Article 22(1) where a receiving third party **draws strongly** on the probability value. Paragraph 72 leaves the national legal-basis and condition checks to the referring court. The Court did not hold that every score is prohibited. |
| **Online declarations of private interests · C-184/20** | [CJEU, Grand Chamber, 1 August 2022](https://juris.curia.europa.eu/juris/document/document.jsf?docid=263721&doclang=EN), ECLI:EU:C:2022:601 | Inspect both operative points: the specified online publication is precluded in the stated respects, and data liable indirectly to disclose sexual orientation constitute special-category processing. This is not a blanket holding against every public declaration. |
| **Meta Platforms / Bundeskartellamt · C-252/21** | [CJEU, Grand Chamber, 4 July 2023](https://juris.curia.europa.eu/juris/document/document.jsf?docid=275125&doclang=EN), ECLI:EU:C:2023:537 | A competition authority's GDPR assessment is subject to sincere cooperation with supervisory authorities. Dominance does not **as such** preclude valid consent, but is an important factor and the operator must prove validity. Read the conditions rather than collapsing the judgment into a slogan. |

These are **issued judgments on references for preliminary rulings**, not Advocate General opinions or model-created enforcement events. The source date, court heading, ECLI, complete paragraph sequence and operative text are verified offline. We do not claim to have audited subsequent national proceedings, later judgments or present legal applicability. English is a translation; the authentic languages of these cases are German, Lithuanian and German respectively. All three judgments predate the AI Act and are not decisions under it.

## Corpus and actual scale

| Pinned source | Edition | Articles | Recitals | Records |
| --- | --- | ---: | ---: | ---: |
| AI Act, Regulation (EU) 2024/1689 | [Adopted text](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng), OJ L 2024/1689, 12 July 2024 | 113 | 180 | 1,678 |
| GDPR, Regulation (EU) 2016/679 | [Adopted text](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng), OJ L 119, 4 May 2016, pp. 1–88 | 99 | 173 | 1,115 |
| Digital Services Act, Regulation (EU) 2022/2065 | [Adopted text](https://eur-lex.europa.eu/eli/reg/2022/2065/oj/eng), OJ L 277, 27 October 2022, pp. 1–102 | 93 | 156 | 1,062 |
| Law Enforcement Directive (EU) 2016/680 | [Adopted text](https://eur-lex.europa.eu/eli/dir/2016/680/oj/eng), OJ L 119, 4 May 2016, pp. 89–131 | 65 | 107 | 580 |
| SCHUFA judgment | English snapshot, 75 numbered paragraphs + one operative point | — | — | 77 |
| Online-declarations judgment | English snapshot, 129 numbered paragraphs + two operative points | — | — | 132 |
| Meta Platforms judgment | English snapshot, 155 numbered paragraphs + eight operative points | — | — | 164 |
| **Total** | **7 official source documents** | **370** | **616** | **4,808** |

The complete record breakdown is 7 documents, 39 chapters, 48 sections, 370 articles, 616 recitals, 13 annexes, 3,581 substantive passages and 134 document-specific definition openings. The 359 numbered judgment paragraphs and 11 operative points are included in the passage count. A numbered judgment paragraph can contain continuation/list blocks; these stay together as one source record.

Links comprise **4,667 `contains`**, **1,234 `references_article`**, **97 `references_annex`**, **134 `defines_term`**, and **1,295 `mentions_term`**. Every count is computed from the actual records and checked on rebuild. No arbitrary words, duplicate decorative nodes or simulated particle counts inflate the atlas. Relative to v1 this adds 2,015 records, approximately 72% more.

## Why these additions matter

The Law Enforcement Directive resolves the second express reference in **AI Act Article 27(4)** to **Directive 2016/680 Article 27**, alongside its distinct **GDPR Article 35** reference. The graph preserves these as different instruments; it does not decide which processing regime governs an actual activity or imply that both regimes apply to the same processing.

The DSA provides a source-reading route through designation, systemic-risk assessment, mitigation, independent audit and data-access provisions: Articles 33, 34, 35, 37 and 40. This is a statutory inspection route, not a platform designation, breach or enforcement finding.

The judgments give a reader source material for testing whether a draft preserves a court's conditions, distinguishes a preliminary interpretation from a national outcome, and carries source context into a handover. They do not demonstrate that TACITUS generation is better. That requires a controlled comparison with matched sources/models and independent domain review.

## Rebuild and verify offline

Python 3.10+ standard library only. No packages, credentials, downloads or model calls:

```sh
python research/ai-governance-source-map/v2/build.py
python research/ai-governance-source-map/v2/verify.py
```

`build.py --output-dir /tmp/tacitus-atlas-v2-check` writes derived outputs elsewhere using the pinned inputs. EU legislation is parsed as XML. A small standard-library `HTMLParser` reads CURIA's public judgment HTML without executing scripts or fetching referenced resources. `verify.py` rebuilds the graph byte-for-byte and checks:

- All seven raw snapshot hashes and normalized-text hashes.
- Every record's exact quote/offset and all node/edge identifiers and domain/range constraints.
- Every literal edge-evidence span, all published counts and the complete CSV record index.
- All 370 articles and 616 recitals, all 359 numbered judgment paragraphs and all 11 operative points.
- Court judgment status, historical event dates and ECLI identities.
- The SCHUFA reliance condition and national-court reservation, the declarations case's indirect-disclosure and publication-scope conditions, and the Meta cooperation and consent qualifiers.
- Explicit instrument resolution, including AI Act 27(4) → GDPR 35 and LED 27; no judgment reference is guessed to refer to the later AI Act.
- Every original v1 file hash in `previous-release-lock.json`, and exact equality of all original v1 graph records.

CI runs v1 and v2 independently. Passing establishes the tested extraction/source-fidelity properties; it does not certify a complete legal ontology or expert-approved legal advice.

## Files and schema

- `graph.json` — `tacitus.source-graph/1`, compatible with the v1 node/edge shape; approximately 4.75 MB uncompressed. Use HTTP compression for the browser.
- `records.csv` — every record's ID, kind, label, document, locator and official source URL.
- `source-lock.json` — full official retrieval URLs, dates, edition/status labels, expected structural counts, byte sizes and SHA-256 pins.
- `sources/*.html` / `sources/*.txt` — unchanged official snapshots and deterministic normalized paragraph-text representations.
- `ontology.json` — application vocabulary, relation constraints and extraction methods.
- `previous-release-lock.json` — immutable v1 preservation receipt.
- `SOURCE_AUDIT.md` / `RIGHTS.md` — source-selection review, edition pitfalls, attribution and reuse terms.

Nodes retain `{id,kind,label,layer,document_id,locator,quote,source_url,source_start,source_end,parent_id?}`. Judgment nodes add `record_role` (`historical_judgment`, `judgment_paragraph`, `judgment_operative_part`); source and case metadata add dates and ECLI. Edges retain `{id,source,target,relation,layer,method,...evidence}`. No new node kind or layer is required by the v1 viewer.

`meta.presets` has seven editorial routes, including `schufa-scoring`, `online-declarations`, and `meta-cooperation-consent`. Each route explicitly labels its editorial status and source IDs. `meta.cases` has three dated case records whose `outcome_node_ids` refer to the exact operative parts. These metadata objects are not extracted edges, legal findings by TACITUS or human approval states.

Useful stable case IDs:

```text
schufa:document
schufa:passage:paragraph:72
schufa:passage:paragraph:73
schufa:passage:operative:1
online-declarations:passage:paragraph:128
online-declarations:passage:operative:1
online-declarations:passage:operative:2
meta-platforms:passage:operative:1
meta-platforms:passage:operative:8
led:article:27
dsa:article:34
```

Offsets are zero-based Unicode code-point `[start,end)` offsets into `sources/{document_id}.txt`, not XHTML bytes or JavaScript UTF-16 indexes. Whitespace is normalized per source paragraph, with two LF characters between paragraphs. Legislative source URLs use existing official anchors. CURIA records use the official document URL without inventing paragraph fragments; locators and exact offsets identify their evidence in the pinned text.

## Material limits

The statutes are **frozen adopted editions, not today's consolidated law**. The selected historical judgments do not repair that gap. Later amendments, corrigenda, guidance, case law, national outcomes and application schedules have not been reconciled.

Legislative containment and judgment structure are extracted. Reference links are conservative, incomplete lexical links, not a complete dependency/precedent graph. Bare legislative references are treated as local; judgment references resolve only explicitly named included instruments or the explicit GDPR abbreviation. Recitals, footnotes, AI Act amending Articles 99–110 and DSA amending Articles 89–90 are not reference-parsed. Ranges retain their written endpoints; “thereof” antecedents are not guessed.

Term matching is literal, case-insensitive and document-specific. Definition records capture their source opening; some definitions continue in following passages. There is no automatic synonymy, cross-instrument identity, inferred obligation, precedential-status model or legal entailment. Original source quirks are preserved; the SCHUFA snapshot, for example, retains a provisional `EU:C:2023:XXX` cross-citation in paragraph 70, which is not resolved into a graph link.

The selection routes are TACITUS-authored reading questions. No independent legal-expert approval, organisation-specific conclusion, privacy guarantee, hallucination reduction or generation benchmark is claimed. Preserve these limits, edition labels, method labels and exact source links when embedding or reusing the data.
