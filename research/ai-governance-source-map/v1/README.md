# AI governance: an inspectable source graph

A reproducible public demonstrator for TACITUS: **2,793 source-linked records and 4,517 typed links**, extracted from two pinned official adopted texts. The browser can explore the full document map and focus on a small selection for one drafting question. This is a working data artefact, not evidence that generation has improved.

**Question:** Before drafting a high-risk AI deployment-assessment note, which source provisions, definitions and qualifiers should an analyst inspect?

The corpus is the English adopted **AI Act, Regulation (EU) 2024/1689**, and **GDPR, Regulation (EU) 2016/679**. These snapshots intentionally preserve the published adopted editions. **They are not the current consolidated legal position.** Amendments, corrigenda, guidance, case law, factual applicability and staged application dates have not been reconciled. Do not use this demonstrator to decide an organisation's compliance obligations.

## What the scale means

| Record | Count | Basis |
| --- | ---: | --- |
| Documents | 2 | Two official publication snapshots |
| Articles | 212 | 113 AI Act + 99 GDPR |
| Recitals | 353 | 180 AI Act + 173 GDPR |
| Chapters | 24 | Published headings |
| Sections | 31 | Published headings |
| Annexes | 13 | AI Act annexes |
| Substantive passages | 2,064 | Actual article/annex XHTML paragraphs, excluding bare list labels |
| Defined terms | 94 | 68 AI Act Article 3 definitions + 26 GDPR Article 4 definitions |
| **Total** | **2,793** | No arbitrary word, duplicate-decoration or particle nodes |

| Link | Count | What it establishes |
| --- | ---: | --- |
| `contains` | 2,697 | Nearest included published structural ancestor |
| `references_article` | 699 | A lexical article reference resolved under the disclosed scope rule |
| `references_annex` | 97 | A lexical reference to a local annex |
| `defines_term` | 94 | A source passage opens this document-specific definition |
| `mentions_term` | 930 | An article contains this literal term phrase; occurrences are aggregated |
| **Total** | **4,517** | Typed extraction links, not 4,517 legal findings |

The full map is a **document/source graph**. A task capsule would retain a much smaller, explicitly selected subgraph with its sources, instructions, versions and human decisions. A smaller selection can make evidence easier to inspect; whether it improves factuality, task quality, latency or token cost requires a separate controlled evaluation. This release supplies no such benchmark result.

## Files and reproducibility

- `graph.json` — compact graph, source provenance, actual counts, limitations and three reading presets. Approximately 2.71 MB uncompressed, 420 KB with deterministic gzip during development; serve normal HTTP compression rather than thousands of SVG elements.
- `records.csv` — the complete public record index, with ID, type, label, locator and official source URL.
- `sources/*.html` — unchanged XHTML downloaded from the official Publications Office's Cellar handler.
- `sources/*.txt` — deterministic paragraph-text extraction, with the exact offset convention documented in graph metadata.
- `source-lock.json` — pinned official publication/retrieval URLs, edition labels, source SHA-256 hashes, byte sizes and retrieval date.
- `ontology.json` — machine-readable application vocabulary, domain/range constraints, methods and interpretation limits.
- `build.py` and `verify.py` — Python 3.10+ standard library only; no package installation, API key, credentials or model calls.
- `RIGHTS.md` — source attribution, EU reuse-policy links and separation of EU source terms from TACITUS code/annotation terms.

Run offline from this directory:

```sh
python build.py
python verify.py
```

`build.py --output-dir /tmp/tacitus-graph-check` writes derived outputs elsewhere while retaining the pinned inputs. The default build never downloads or silently refreshes a legal text. To revise an edition, add a new version folder and source lock, review source identity/rights and edition scope, then rebuild and compare the changed records. Do not overwrite `v1`'s evidence to make it look current.

The verifier checks raw source integrity, expected article/recital counts, every quoted source span, node/edge uniqueness, relation domains/ranges, literal evidence spans, all preset IDs, all public counts, the record index and a byte-for-byte rebuild. Specific regressions prevent the AI Act Article 27(4) reference to **Directive (EU) 2016/680 Article 27** from being falsely linked to AI Act Article 27. The same sentence's explicit **GDPR Article 35** link is retained. Qualified Article 4 references in AI Act definitions are also kept in the correct instrument.

Passing these checks establishes reproducibility and the tested source-fidelity properties. It does not establish a complete legal ontology, expert approval or correctness of an AI-generated answer.

## Schema and integration

```text
graph.schema = "tacitus.source-graph/1"
graph.meta = { title, case_question, built_on, edition_scope,
               counts, sources, offset_convention, presets,
               review_state, limitations }
graph.nodes[] = { id, kind, label, layer, document_id, locator,
                  quote, source_url, source_start, source_end,
                  parent_id? }
graph.edges[] = { id, source, target, relation, layer, method,
                  source_locator?, evidence_node?, evidence?,
                  match_start?, match_end?, occurrences?, passage_count? }
```

`source_start` and `source_end` are zero-based **Unicode code-point** offsets into the corresponding normalized `.txt` snapshot. They are not raw HTML byte offsets. `quote` must equal that exact substring. Per-paragraph whitespace is normalized with Python `str.split()`, paragraphs are separated by two LF characters, and the file ends with one LF. Source spelling and oddities are retained, not silently corrected.

For lexical reference edges, `match_start`/`match_end` index the source passage's quote. For `mentions_term`, they index the first matching passage named by `evidence_node`. A term edge is aggregated at article level, with `occurrences` and `passage_count`; it does not assert that every occurrence uses the same legal sense.

Stable article container IDs:

```text
ai-act:article:6
ai-act:article:14
ai-act:article:26
ai-act:article:27
gdpr:article:35
```

Article/annex passage nodes carry `parent_id`, and `contains` links expose the entire hierarchy. For example, `ai-act:passage:027.004` is the exact AI Act Article 27(4) paragraph; `gdpr:passage:035.002` preserves **“where designated”** in its data-protection-officer advice requirement. `ai-act:passage:027.001:p06` is the human-oversight description item in Article 27(1)(e).

Some official XHTML paragraph IDs are reused inside amendments quoted in other articles. Local record IDs add `:in-art_107` (for example) to disambiguate; their source link points to the containing article, and exact text offsets remain authoritative within this snapshot. Generated `:pNN` locators transparently indicate extraction order, not invented official legal numbering.

## Three useful inspection routes

`meta.presets` contains `{id, label, title, question, description, start_id, node_ids}`. These are **authored reading questions outside the extracted graph**, with no reviewed-interpretation or applicability claim.

1. **Before drafting an assessment.** Compare AI Act Article 6's classification, Article 26's deployer provisions, Article 27's scope and exceptions, and the explicit Article 27(4) link to GDPR Article 35. Article 27 does not simply apply to every AI deployment; the complete source wording matters.
2. **Trace human oversight.** Inspect AI Act Article 14's design/development provision, Article 26(2)'s deployment provision and Article 27(1)(e)'s assessment-description item. Preserve their different roles and conditions.
3. **Keep the qualifier.** Inspect GDPR Article 35(2) alongside Articles 37 and 39. A generated draft that drops “where designated” can change the meaning; the graph exposes the source but does not decide whether an actual organisation must designate a DPO.

The UI should show exact quotes, method, source edition and official source links on selection. Keep structure, lexical references and terminology visually distinct. If a team later adds a conclusion, disagreement or reviewer decision, store it as an attributed, versioned annotation with its own evidence and approval state. Never present a lexical edge, inferred annotation or illustrative route as an approved legal finding.

## Deliberate extraction limits

- Reference extraction scans article and annex body passages, not recitals or footnotes. AI Act Articles 99–110 insert amendments into other instruments and are deliberately excluded from reference resolution.
- Explicitly named foreign instruments other than these two pinned texts are omitted, rather than guessed. Bare references in operative passages are treated as local to their source instrument; this disclosed heuristic remains incomplete and requires expert review for legal use.
- Written article lists are tokenized; written ranges retain their endpoints only. Paragraph/point references are not expanded into inferred dependencies. “Thereof” antecedents are omitted rather than scope-guessed; references through other antecedents, other languages and unusual constructions can be missed.
- Terms remain document-specific. Matching is literal, case-insensitive, singular-phrase and whole-word-boundary only. There is no stemming, synonym expansion, entity alignment, embedding similarity or legal entailment.
- All public source records are real. The demonstrator contains no private/customer data, staged team discussions, fake approval states, automatically invented legal interpretations or fabricated benchmark gains.

These limits are material to the experiment: source structure supports inspection and bounded context selection, while expert interpretation, generation, and evaluation remain separate engineering and research tasks.
