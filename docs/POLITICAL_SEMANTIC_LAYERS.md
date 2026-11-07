# Political semantic layers: a runnable teaching example

This example turns a small, curated selection of real source wording into queryable,
attributed records. It supplies a common vocabulary, four task lenses, five recurring
task recipes, JSON-LD and a local SQLite export. Python 3.10+ is sufficient; no model,
API key, package installation or network request is needed to run it.

It is a bounded extension under `examples/political_semantics/`, not a replacement for
the canonical TACITUS or Syria schemas. The local vocabulary uses
`urn:tacitus:political-demo:`. It is not a published ontology or a claim of equivalence
with any legal or political terminology system.

## Run it

From the repository root:

```bash
python examples/political_semantics/semantic_layer.py validate
python examples/political_semantics/semantic_layer.py query --lens mediation
python examples/political_semantics/semantic_layer.py query --lens policy_analysis --published-by 2016-01-01
python examples/political_semantics/semantic_layer.py query --lens media_narrative --include-drafts
python examples/political_semantics/semantic_layer.py query --lens hr_policy --include-drafts
python examples/political_semantics/semantic_layer.py recipes
python examples/political_semantics/semantic_layer.py export --out /tmp/political-demo.jsonld
python examples/political_semantics/semantic_layer.py export-sql --out /tmp/political-demo.sql
python -m unittest discover -s tests -p test_political_semantics.py -v
```

Validation reports 5 sources, 10 semantic records and 0 human-reviewed records. The
default mediation query returns 5 records. The default media query returns 2 records
about published wording and attribution; `--include-drafts` also returns 2 analyst
annotations. The default HR query returns no records because the ILO extraction
remains a candidate; the explicit draft option reveals its applicability checklist.

`--corpus /path/to/selection.json` before the command loads another selection in the
same format. Lenses and recipes are editable metadata in `corpus.json`; record lens
tags determine selection. Queries do not assign relevance, saliency or bias scores.
The `--published-by` option filters the consulted source's publication date only.
It does not reconstruct what a person knew at the time, filter ingestion time, or
determine which legal provisions were in force. Year-only dates, if supplied, are
admitted only after the whole year has elapsed.

## Retained evidence and its limits

| Source | What is represented | Check and locator |
| --- | --- | --- |
| [UN Security Council resolution 2254 (2015)](https://documents.un.org/doc/undoc/gen/n15/443/34/pdf/n1544334.pdf) | The Council's endorsement of the Geneva communiqué and its expressed position on Syrians deciding their country's future | Official English PDF downloaded and inspected; operative paragraph 1, page 2/4 |
| [Geneva communiqué, reproduced in resolution 2118 (2013)](https://documents.un.org/api/symbol/access?l=en&s=S/RES/2118(2013)&t=pdf) | The communiqué date and the mutual-consent condition for the transitional governing body described in paragraph 9(a) | Official English PDF inspected; annex II heading on page 9/13 and paragraph 9(a), page 11/13 |
| [UN Guidance for Effective Mediation](https://documents.un.org/api/symbol/access?l=en&s=A/66/811&t=pdf) | Guidance on consent in voluntary mediation | Official English PDF inspected; A/66/811*, annex I, paragraph 21, page 23 |
| [Reuters, 16 December 2024](https://www.reuters.com/world/middle-east/un-envoy-meets-syrias-sharaa-urges-inclusive-transition-2024-12-16/) | A short headline and a phrase Reuters attributes to a General Command statement | Direct article inspection; headline/byline and second paragraph. The original attributed statement is not retained |
| [ILO Convention No. 190](https://www.ilo.org/dyn/normlex/en/f?p=NORMLEXPUB%3A12100%3A0%3A%3ANO%3A%3AP12100_INSTRUMENT_ID%3A3999810) | Candidate extraction of article 6's equality and non-discrimination provision | Official indexed text only; direct retrieval returned a redirect loop. Excluded from default evidence queries |

The 2254 source reuses the original official PDF URL and receipt identity from the
[Syria corpus at commit 4d7c6ec](https://github.com/sargonxg/Syria-political-analysis/blob/4d7c6ec55c1a1435cd7449b6e02d5640205f0d89/data/documents/receipts.json),
record `doc-83ad8cbb868c0c88`. A fresh download matched its stored PDF SHA-256.
The demo references that corpus rather than importing its full dataset or changing
its review decisions.

Each retained excerpt carries the source URL, symbol where relevant, publication
date, locator and SHA-256 of its exact retained UTF-8 text. PDF line/layout whitespace
is collapsed; this is recorded explicitly. Three `original_sha256` values identify
the original downloaded PDF representations, which are not bundled. Excerpt hashes
check local integrity, not authenticity of a remote source or accuracy of a summary.
The Reuters retention is limited to a headline and a five-word attributed phrase;
no full article or article-wide factual verification is provided.

Example code follows this repository's Apache-2.0 license. Retained third-party
wording remains attributed to its original sources and is not relicensed as
TACITUS-authored text. The short selections do not grant rights to redistribute
the full documents or articles; consult source terms for a larger corpus.

`source_verified` means an automated agent checked the retained wording against the
directly accessed source representation. It does **not** certify a record's analyst
paraphrase, real-world truth, implementation, legal effect, or human approval.
`candidate` is unverified source material; `analyst_draft` is interpretation, including
alternative motive questions. Default queries exclude both. All included records
have `human_reviewed: false`. A future `human_reviewed` state requires an explicit
reviewer identity, UTC review time and approved decision as well as the flag;
the example cannot authenticate that person's identity.

## Common core and task-specific questions

Actors have roles such as issuer, publisher, byline, reported speaker or analyst.
They are not conflated. Evidence stores a short representation and locator. Claims,
interests, constraints, commitments, events and narratives link back to that evidence.
An interest can be an expressed normative objective without claiming a population's
empirical preferences. A commitment record here captures institutional endorsement,
not an implemented agreement or proof that a conflict party undertook an obligation.

Records preserve authority, source modality, adopted/issued/proposed document stage,
implementation status, attribution chain, review state and scope. Publication belongs
to a source; event occurrence, validity bounds and recording time are separate fields.
The communiqué's original 2012 date is retained separately from the consulted
resolution carrier's 2013 publication date. Unknown validity remains unknown.

| Recurring task | Lens | Expected output and review |
| --- | --- | --- |
| Resolution brief | `policy_analysis` | Attributed clauses with modalities and missing implementation evidence; review authority and dates |
| Communiqué comparison | `policy_analysis` | Clause comparisons with issuer, original date and carrier publication; review whether endorsement changes the wording |
| Mediation preparation | `mediation` | Questions about dated consent, representation, interests, constraints and inclusion gaps; obtain party-specific evidence |
| Media framing review | `media_narrative` | Attributed wording and competing frame interpretations; construct a matched sample before wider conclusions |
| HR policy application | `hr_policy` | Evidence checklist for ratification, jurisdiction, domestic law, worker scope and organization rules; obtain appropriate human review |

Recipe metadata lists required evidence fields as an **input checklist**, not a claim
that this small corpus already supplies them. No employer duties are determined.
No media owner, ideology, motive or ownership influence is inferred: the Reuters
ownership field is explicitly unassessed. A single selected headline cannot establish
outlet-wide bias. Motive questions retain alternatives and stay in analyst drafts.

## Queryable exports

JSON-LD represents actors as `prov:Agent`, retained documents/excerpts/records as
`prov:Entity`, evidence derivation as `prov:wasDerivedFrom`, attribution as
`prov:wasAttributedTo`, and local concepts as `skos:Concept`. Detailed qualifications
remain JSON-LD 1.1 JSON literals, preserving their boundaries instead of silently
dropping them. No `owl:sameAs` assertions or asserted external concept matches are
generated. Consumers must understand the local vocabulary and review states.

The SQL dump creates only `policy_semantic_*` tables and a
`policy_semantic_verified_assertions` view. It preserves sources, retained evidence,
assertions, actor roles, lens memberships and recipes, with foreign keys and indexes.
Load it into a **new local database**, for example using Python's standard library:

```python
import sqlite3
from pathlib import Path

with sqlite3.connect('/tmp/political-demo.sqlite') as db:
    db.executescript(Path('/tmp/political-demo.sql').read_text())
    assert not db.execute('PRAGMA foreign_key_check').fetchall()
    rows = db.execute('''
        SELECT a.id, a.statement, a.review_state
        FROM policy_semantic_verified_assertions a
        JOIN policy_semantic_assertion_lenses l ON l.assertion_id = a.id
        WHERE l.lens_id = ? ORDER BY a.id
    ''', ('mediation',)).fetchall()
    print(rows)
```

The base tables retain candidates and drafts for review; use the view when starting
from checked source wording. Every database connection that writes should enable
`PRAGMA foreign_keys=ON`; database consumers must also apply review-state policy.
The Python validator checks quotes, hashes and semantic boundaries before export;
SQL foreign keys alone cannot enforce all those semantics after arbitrary edits.
The SQLite dump is an inspectable local integration example, not a tested D1 migration,
live dataset update, or part of a frozen production snapshot. Repeat imports into the
same populated database are deliberately not an upsert strategy.

Tests cover dangling references, hash/quote tampering, human-review metadata, source
verification gates, attribution chains, temporal separation, rejected implementation
and bias overclaims, default draft exclusion, deterministic JSON-LD, and local SQL
foreign-key/integrity checks. No improvement in generated AI output is claimed without
a separate evaluated task set and human-reviewed reference answers.
