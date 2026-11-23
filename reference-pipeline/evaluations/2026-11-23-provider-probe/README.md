# Six live provider checks — 23 November 2026 UTC

Six approved synthetic requests completed through the Cloudflare Workers AI REST API: flat and graph-annotated context for Gemma 4, GPT-OSS 120B and GLM 5.3. **All six returned schema-valid final answers with resolving citation IDs. These are provider compatibility probes, not App/Gateway acceptance or evidence of general answer-quality improvement. Generation remains paused.**

The task asks whether a licence renewal was approved. Source e1 permits a six-month renewal only if an independent reviewer accepts the risk note. Source e2 records an objection that the note is incomplete and no final approval. Both arms use the same sources, question and 1,024-completion-token limit; the structured arm adds relationship annotations.

| Model | Flat context | Graph-annotated context |
| --- | --- | --- |
| Gemma 4 | Preserved objection/no approval; omitted the requested condition and cited only e2. | Preserved condition, duration, objection and no approval; cited e1/e2. |
| GPT-OSS 120B | Preserved condition, duration, objection and no approval. | Preserved the same material facts. |
| GLM 5.3 | Preserved condition, duration, objection and no approval. | Added “only proposed”, a stronger procedural status than the permission source establishes; omitted duration. |

These observations come from unblinded, post-hoc assistant review. No independent human approval or statistical inference is claimed. The graph's `proposed_action` label is an annotation, not an additional source fact; its possible influence is a reason to test graph fidelity. The duration omission is an additional observation, not a preregistered pass/fail criterion.

## Cost and reproducibility

The six responses reported **1,257 prompt tokens and 450 completion tokens**. At the observed catalogue rates, the conservative estimate without cache discounts is **$0.0015707**, within the approved $0.25 ceiling. This is a usage-based estimate, not a verified invoice. No request was repeated.

`plan.json` contains the exact prepared requests and their SHA-256 hashes. Each `*.result.json` contains its final answer, requested/reported model identity, usage, timestamps and request hash. Provider-private reasoning fields are omitted; an original normalized-response digest is recorded. `report.json` contains the review and explicit scope limits.

Gemma's reported identifier ends in `-external`; the record preserves that alias without asserting a hardware or vendor placement. Direct REST execution does not validate the deployed AI Gateway route, authenticated App dispatch, document-writing role, multilingual tasks, local weights or customer-scale performance.

## Next acceptance work

Preserve mandatory task conditions even when an answer cites a different valid source. Validate graph status annotations against their exact support and keep interpretations distinct from evidence. Then test actual App/Gateway paths, multiple held-out tasks and independent reviewers, without treating these six probes as an activation receipt. No additional inference is authorised by this record.
