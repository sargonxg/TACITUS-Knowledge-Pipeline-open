# A guided workflow

The runnable CLI verifies sources, validates the ontology, applies a semantic layer, prepares bounded context and renders an evidence-review sheet. It also emits a workflow plan with a final human-review stage and explicit stop conditions.

A compatible agent could invoke these tools before asking a model to draft. The plan has no permission to send messages, make purchases, deploy services or approve an analysis. The current tool executes none of those actions and makes no model calls.

External model adapters, reviewer identity, approval persistence and a tested PRAXIS bridge are work in progress. PRAXIS itself is invitation-only and generation is paused. A downloaded JSON file is not evidence of a working agent integration.
