# TACITUS local companion

Choose an installed Ollama or LM Studio model in the authenticated TACITUS App. The companion lists local-server models, receives a single authorised request, calls your configured loopback inference server, and returns a schema-checked result. Node 24+; no package dependencies. It downloads no weights and runs no generated code or tools.

Start your local inference server yourself. Clone this repository, then:

```sh
node local-companion/client.mjs models --provider ollama
```

In `https://app.tacitus.me/`, sign in, open a conversation, then **Model connections → Pair a computer**. Copy its one-time code and use it on your computer:

```sh
node local-companion/client.mjs pair --app https://app.tacitus.me/ --code YOUR_PAIR_CODE --provider ollama
node local-companion/client.mjs run
```

For LM Studio, use `--provider lmstudio`; start its server and load a model first. Defaults are `http://127.0.0.1:11434/v1` for Ollama and `http://127.0.0.1:1234/v1` for LM Studio. `--endpoint` accepts only a loopback HTTP `/v1` URL. `--context` declares the server's configured context window (default 8192); use a value your machine and loaded model actually support. Ollama's reported maximum further bounds it, and the native request sets `num_ctx` and `num_predict`. Configure LM Studio's loaded context window to match your declared `--context`; its OpenAI-compatible endpoint does not reconfigure the loaded model. Context estimates are conservative byte-based estimates, not exact tokenizer counts. Small models can refuse a large task before inference.

Refresh Model connections in the App to see the paired models. Pick one in Conversation or Writing. Both hosted and local generation follow the workspace's generation control; pairing and model discovery remain usable while generation is paused. Generation is currently paused in the hosted App. Specialist multi-step research tools use their own provider acceptance and are not executed by this companion.

The companion stores its narrowly scoped bearer token and private job recordings under `~/.config/tacitus-local` with restricted permissions. Use `--state-dir` for another directory. A token is bound to one user, workspace scope and connection. Revoke it in the App when finished. It does not provide general account or library access. The companion initiates outbound App requests; your inference server needs no public tunnel.

Inference requests go to the configured loopback endpoint. Model weights, remote model bridges and actual hardware are under your control; a loopback transport cannot independently prove their placement. Ollama cloud-model metadata is excluded. This is not an offline-storage mode: selected context comes from the hosted workspace, and accepted responses are stored there. Private request recordings also remain on your computer.

The companion retains each claim before inference. It never automatically repeats an uncertain model call. On restart it can resend a retained result delivery idempotently. Cancellation, revoked access, changed source context and expired jobs prevent acceptance of a late result. An HTTP disconnect cannot guarantee that a local server has stopped consuming compute.

Protocol and loopback integration tests use synthetic model responses. Real installed-weight and hardware acceptance must be recorded separately. Successful transport, valid JSON and resolving citation IDs do not prove factual support or model quality.
