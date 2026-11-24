# Model-facing context from a real source graph

Select a source-atlas reading route and obtain one **standalone context packet** that a person can attach to a chosen model or hand to another analyst/agent. It contains the task, complete selected source passages, edition identities, qualifications, open questions and review state. The next conversation can receive the same evidence without reconstructing it from headings or a picture of a graph.

This is an additive, offline compiler for the seven frozen [atlas v2](../v2/README.md) routes. It makes no model calls, enables no hosted generation and changes no source graph or paper. A packet is model input, not a generated answer, an organisation-specific legal conclusion or an approved human interpretation.

## What the compiler does

1. Check the released graph SHA-256 and all seven official raw/normalized source snapshot hashes.
2. Start from the route's exact editorial source selections. Treat article/document headings as navigation; do not count them as substantive evidence.
3. Expand each selected article through its real `contains` links to **all** direct body passages, including lead-ins, points, conditions and exceptions. Retain explicitly selected judgment paragraphs and operative points whole. A document heading does not silently select an entire judgment or corpus.
4. Carry exact quoted records, Unicode source offsets, official URLs, locators, source editions, rights notices and raw/extracted source hashes into the packet. Source records are exact copies of the released graph nodes.
5. Include retained lexical-reference edges, while distinguishing outside-packet pointers from supplied evidence. Record every expansion and the full selection so a reviewer can reproduce the handover.
6. Include 21 source-wording checks across the routes, including SCHUFA's strong-reliance and national-court conditions and GDPR's **“where designated”** qualifier. The full records remain the evidence; the short check fragments do not replace them.
7. Measure the complete canonical UTF-8 packet against a finite **98,304-byte (96 KiB)** budget. If it cannot fit, fail before writing; never clip a source quotation or silently omit part of the requested body. Successful output is written with a unique temporary file in the destination directory, atomically replaced, and cleaned up.

This gives the graph a concrete assembly job: stable source identities and containment recover the selected provision's actual body and preserve a reproducible evidence set. A carefully prepared flat prompt containing the same evidence could communicate the same information. This release does **not** show that a graph improves model answers relative to that comparator.

## Use it

Python 3.10+ standard library only; no package installation, credentials, downloads or inference:

```sh
python research/ai-governance-source-map/context-packets-v1/build.py
python research/ai-governance-source-map/context-packets-v1/verify.py
```

`packets.json` is the one compact grouped publication. Choose exactly `bundle.packets[routeId]` and serialize that object to download or attach **one standalone packet**. This represents the selected **editorial route**, including its complete article-body expansions; it is not a capture of arbitrary graph hover, search or zoom state.

For example, from the repository root:

```python
import json
from pathlib import Path

bundle = json.loads(Path(
    "research/ai-governance-source-map/context-packets-v1/packets.json"
).read_text(encoding="utf-8"))
packet = bundle["packets"]["schufa-scoring"]
Path("/tmp/schufa-context.json").write_bytes(json.dumps(
    packet, ensure_ascii=False, sort_keys=True, separators=(",", ":")
).encode("utf-8"))
```

Give a chosen model this JSON and its `editorial_context.question`, or adapt the question while keeping the source and change history. Ask for a short source-linked explanation and a clear statement of missing facts. Inspect the answer separately: a correct packet does not make the answer correct. Changes to the packet require a new checksum and an honest review state; the published checksum identifies the original input, not a subsequently edited version.

The public website integration copies `packets.json` unchanged to `/assets/atlas-packets.v2.json`. The grouped file is a transport resource; the UI should fetch it only following an explicit request, validate the source graph/route/evidence and checksum, then download the chosen route packet. Neither download nor verification makes an AI call or writes to an App workspace.

## Actual assembly measurements

These are byte counts and source-fidelity checks, not tokens, semantic coverage scores, generation results or cost savings.

| Route ID | Substantive records | Source-quote UTF-8 bytes | Complete packet bytes | Required wording checks |
| --- | ---: | ---: | ---: | ---: |
| `assessment-boundaries` | 72 | 20,539 | 68,220 | 5 |
| `human-oversight` | 44 | 13,299 | 43,284 | 3 |
| `qualified-advice` | 35 | 7,538 | 31,682 | 3 |
| `schufa-scoring` | 39 | 9,881 | 38,218 | 3 |
| `online-declarations` | 40 | 12,138 | 41,200 | 2 |
| `meta-cooperation-consent` | 46 | 14,614 | 46,332 | 3 |
| `dsa-systemic-risks` | 91 | 26,222 | 73,982 | 2 |

All seven fit the declared 96 KiB budget. No requested or expanded body passage is omitted, and no quote is shortened. The 367 evidence-record appearances span **266 unique graph records**; repetitions are intentional because each packet is independently usable. Navigation is counted separately. The longest retained quote is 1,852 UTF-8 bytes; none exceeds the disclosed 4,096-byte long-record threshold. Longer future records must remain whole or cause an explicit budget failure in a new release.

The grouped publication is **343,904 bytes**, approximately **67,830 bytes with gzip**. Its SHA-256 is `98485a5e4aa3ca777955ed1c03053aa4541113a6dae7bcf131037b41df7998b9`. A model provider may tokenize the JSON differently; apply its actual context limits before running it. No output-quality comparison is reported, including against a deliberately weak heading-only or first-bytes baseline.

## Bundle and standalone schema

```text
bundle.schema = "tacitus.public-route-packets/1"
bundle.source_graph = { release, schema, sha256, repository_commit, path, url }
bundle.packets = { [exact atlas preset ID]: standalonePacket }

packet.schema = "tacitus.model-context-packet/1"
packet.id = exact atlas preset ID
packet.editorial_context = original route + explicit editorial role
packet.task_boundary / open_questions / instructions / review
packet.sources = { [document_id]: exact released source metadata }
packet.navigation[] = original heading identity + heading_quote + navigation_only role
packet.records[] = exact full substantive passage nodes from graph v2
packet.relations[] = exact retained lexical-reference edges
packet.selection = requested IDs, article expansions, retained IDs, outside pointers,
                   required qualifiers, budget and no-clipping policy
packet.measurements = integer counts and UTF-8 byte measurements
packet.integrity = { algorithm, canonicalization, sha256 }
```

`selection.requested_node_ids` preserves the route's original ordered `node_ids`. Evidence order is deterministic by `(document_id, source_start, id)`, so it differs from the route's navigation order. `selection.retained_record_ids` exactly matches `records[].id`. Each record retains its original `document_id`, `quote`, `source_url`, `locator`, `source_start` and `source_end`; offsets refer to the released normalized source text in Unicode code points, not UTF-8 bytes or browser UTF-16 indexes.

`sources` is keyed by the union of evidence and navigation document identities. Each value is the exact corresponding graph source entry, including its edition and both raw/extracted SHA-256 pins. `relations` contains reference edges only: `parent_id` and explicit navigation expansion lists already preserve structural containment. An editorial route is not asserted to be an automatically discovered legal dependency or precedential relationship. Outside-packet reference targets are labelled pointers without supplied evidence.

## Checksum convention and independent checks

The frozen graph SHA-256 is `31841211f001820b43cf3fbe9f209cd3cf1d70a6a26b5bef7a9c6b20f05680a6`, pinned to public repository commit `b96550da802c2992577142016245c6453d937e8b`. The builder refuses a changed source graph or changed official snapshot rather than silently adopting it.

For a packet's independent checksum, remove its entire `integrity` field, recursively sort object keys, encode compact JSON with literal Unicode and no trailing LF, then hash its UTF-8 bytes with SHA-256. Object keys are ASCII; all numeric fields are integers, allowing equivalent browser serialization. `measurements.packet_utf8_bytes` measures the **full** canonical packet including integrity. Its size field is resolved to a fixed point before hashing. A checksum is not a truth or approval certificate.

`verify.py` independently checks exact node equality, original source spans and hashes, genuine complete article-body expansion, editorial/navigation boundaries, exact retained references, all seven route IDs, byte counts, budgets, qualifiers and per-route checksums. It also rebuilds the grouped output byte-for-byte. Regression checks reject:

- A fabricated source quote even after a new syntactically valid packet checksum is computed.
- Loss of SCHUFA's reliance/national-court reservations, GDPR designation wording, the AI Act profiling override, LED scope, declaration-publication limits, Meta cooperation/consent qualifiers, and DSA designation conditions.
- An insufficient budget that would otherwise clip text; the previous output remains untouched.
- A changed official judgment snapshot.

Two concurrent rebuilds to the same output are tested for exact final bytes and unique-temporary-file cleanup. CI runs the compiler verifier after atlas-v2 verification. The historical graph releases and papers remain untouched.

## Limits and source rights

The evidence consists of frozen adopted EU texts and selected historical English CJEU judgment translations. It is not current consolidated law, a complete legal analysis, a completed national-case outcome or private team memory. Outside provisions, current amendments, factual deployment/service details, national rules and later judgments may be essential to a real answer. The packet asks the model to leave those gaps open.

Every packet is labelled **not expert-approved**. The source wording checks establish assembly fidelity, not that a model will preserve meaning. Preparing and reviewing context costs time; no total-cost, hallucination-reduction or generation-quality improvement is established. A useful evaluation must compare matched models/source access against capable flat, retrieval and full-document inputs and include preparation, update and reviewer effort.

Source text, attribution and EU/CJEU reuse terms remain as recorded in the [v2 rights notice](../v2/RIGHTS.md). Original compiler/validation code and authored task guidance follow the repository's licensing. No user files, private discussions, model-generated answers or fabricated approval states are included.
