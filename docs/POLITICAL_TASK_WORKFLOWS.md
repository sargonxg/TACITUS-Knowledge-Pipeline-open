# Five offline policy research workflows

Python 3.10+ and its standard library are sufficient. From a clean checkout:

```sh
git clone https://github.com/sargonxg/TACITUS-Knowledge-Pipeline-open.git
cd TACITUS-Knowledge-Pipeline-open
python examples/political_semantics/task_workflows.py --out task-output
python examples/political_semantics/task_workflows.py --verify task-output
python -m unittest discover -s tests -v
```

These commands also work in PowerShell. Choose a fresh output directory: the
exporter refuses to overwrite prior work. It uses the committed attributed
teaching corpus, with no downloads, paid APIs, inference or database service.

## Choose the work

| Task flag | Inspectable result | Essential unresolved question |
| --- | --- | --- |
| `resolution_brief` | Resolution clauses, attribution, legal verbs and source locators | Is there evidence of implementation beyond endorsement? |
| `communique_comparison` | Communiqué-related wording with dates, sources and exact excerpts | Is the same clause being compared, and what does endorsement establish? |
| `mediation_preparation` | Consent and inclusion evidence with party references | Whose consent, mandate or representation is still unverified? |
| `media_framing_review` | Retained reporting and its attributed assertions | Is this sample sufficient for any wider claim? It does not detect media bias. |
| `hr_policy_application` | Convention wording and an unresolved applicability checklist | Which jurisdiction, ratification, national law and workplace rules apply? |

For one task:

```sh
python examples/political_semantics/task_workflows.py --task mediation_preparation --budget-bytes 6000 --out mediation-output
python examples/political_semantics/verify_packet.py mediation-output/mediation_preparation.inspection.json
```

`--published-by YYYY-MM-DD` is a source-publication filter. It does not establish
when an event occurred, when a rule became legally applicable or what an analyst
could actually have known at that date. The original temporal fields remain in
the packet. Some short publication metadata only has year precision.

## Inspect the files

Each task has a Markdown worksheet, a JSON worksheet, an inspection wrapper
containing the packet and receipt, and an exact compact `.packet.json` payload.
The worksheets reproduce source assertions and quotations. Analyst interpretation
is null, hypotheses are empty, approval is `not_reviewed`, and required evidence
checks remain unresolved. These files prepare a review; they are not completed
briefs or legal assessments.

The manifest records every output's exact bytes and SHA-256. Verification
reconstructs each task from the retained corpus and checks passages, references,
review fields, selection, omissions, payload variants and budget comparisons.
Changing a quotation and updating its local hash does not pass verification
against the original corpus. A maliciously changed corpus still requires source
criticism: these hashes establish reproducibility, not truth or trusted authorship.

`budget-comparison.json` measures selection at 4,000, 8,000 and 16,000 bytes and
the chosen budget. It lists omitted IDs and reasons and retained primitive types.
Only compact packet bytes count toward that budget. Worksheets, manifests and
receipts add overhead. No model token estimate, cost saving or reasoning benefit
is inferred from a smaller packet.

[Committed worked outputs](../examples/political_semantics/worked_tasks/manifest.json)
can be inspected before installing anything. The five task outputs use a small
curated corpus of five sources, not a comprehensive research collection. Source
passages retain their original attribution and rights notes; the repository's
software license does not relicense third-party text.

This teaching format is separate from native TACITUS Context JSON, DIALECTICA
capsule bundles and PRAXIS promotion. It does not silently import into any of them.

On Windows, checks were executed with Python 3.12: 45 tests passed, all five
packages were generated and verified offline. No model-backed evaluation ran.
