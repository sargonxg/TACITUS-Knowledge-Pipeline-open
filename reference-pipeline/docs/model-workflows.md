# Source → capsule → model draft → review

This path performs actual model generation when explicitly requested. The offline `build` command still makes zero model calls. The example is a historical negotiation-policy desk note from Security Council resolution 2254 (2015), not a current Syria assessment.

## Build the case

From `reference-pipeline`:

```sh
PYTHONPATH=src python -m tacitus_pipeline build \
  --input examples/syria-negotiation/collection.json \
  --ontology ontology/negotiation.json \
  --layer layers/syria-negotiation.json \
  --question "Prepare a negotiation-policy note: who was asked to do what, which historical timetables and conditions matter, and what remains unverified?" \
  --output build/syria
```

## Generate a cited draft

Use an already running local Ollama server and an installed model that supports JSON output. Select the exact installed model; the example name is not downloaded by this command.

```sh
PYTHONPATH=src python -m tacitus_pipeline.workflow generate \
  --bundle build/syria --provider ollama --model llama3.2:3b \
  --output build/syria-draft
```

Alternatively use `--provider cloudflare --model @cf/meta/llama-3.3-70b-instruct-fp8-fast`, with `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_API_TOKEN` configured outside Git. Or use `--provider openai-compatible --model YOUR_MODEL --endpoint https://YOUR_PROVIDER/v1/chat/completions`, with `TACITUS_MODEL_API_KEY` configured outside Git. Remote custom endpoints require HTTPS; redirects are refused. Provider usage and costs apply. There is no automatic provider fallback or retry.

The Cloudflare model was actually executed for the committed recordings. The Ollama/OpenAI-compatible HTTP adapters were exercised against a loopback test server; a live Ollama model was not installed or tested for this update. See [Ollama's compatibility contract](https://docs.ollama.com/api/openai-compatibility).

## Run the bounded agent

```sh
PYTHONPATH=src python -m tacitus_pipeline.agent run \
  --bundle build/syria --provider cloudflare \
  --model @cf/meta/llama-3.3-70b-instruct-fp8-fast \
  --output build/syria-agent
```

The model first chooses `inspect_evidence` IDs from the selected capsule. Code resolves those IDs, returns exact source text, and records the step. A later model step can propose a cited draft. Drafting before inspecting required evidence is refused. The agent permits at most four model steps and no shell, arbitrary URL, publication or approval action. Model calls are nondeterministic even when temperature is zero; only validation and evidence assembly use fixed rules.

## Inspect an actual run

The committed [two-step agent result](../examples/syria-negotiation/agent-step-2/workflow-result.json) and [draft](../examples/syria-negotiation/agent-step-2/draft.md) were produced with Cloudflare on 10 November 2026. Requests, raw responses and step states are retained beside them. The first protocol attempt was refused and is retained under `agent-refused-attempt`; the corrected run actually inspected evidence before drafting.

Open `workflow-result.json` in [TACITUS Workbench](https://github.com/sargonxg/tacitus-workbench), using its **Policy briefing** mode. It checks the capsule checksum, source editions, citation attachments and qualification spans, and exports the imported JSON unchanged. It is a reader, not a model executor. The result is a separate pipeline format; it is not a native Context, DIALECTICA capsule or verified PRAXIS attachment.

## Review what the checks establish

A cited ID must resolve to a selected statement. Exact quotations and declared qualifications are attached by code, rather than rewritten by the model. Required evidence identities must be covered. Extra action/approval fields, invalid JSON, unfinished outputs and unknown citations are refused. A literal flag highlights qualifications absent from the draft wording; it cannot determine whether a paraphrase preserves their meaning.

These checks do not prove entailment, current applicability or expert approval. Read the source wording. All outputs remain `draft_for_human_review`.

## Reproduce without a model account

Use `workflow prepare` or `agent prepare` to export the exact request. `workflow import` or `agent advance` accepts an explicitly recorded provider response bound to that request's checksum. Importing a recording is not a fresh model call and does not authenticate the transport or reported usage. Unit tests replay the actual committed responses without contacting a provider.

## Efficiency result

The single frozen task produced 1,280 reported tokens for flat evidence and 1,889 for structured evidence. The structured draft was shorter, but total usage was higher. The two-step agent used 2,427 reported tokens. These are smoke-test observations on one model and task, with different context representations; they do not establish a general quality, latency or efficiency gain. See [the comparison notes](../../research/README.md) and the model-evaluation plan for the controlled work still required.
