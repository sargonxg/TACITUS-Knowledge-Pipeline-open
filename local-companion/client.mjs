#!/usr/bin/env node
// TACITUS local companion. Only user-configured loopback inference; no tools or shell execution.
import { readFile, writeFile, mkdir, readdir, rename } from "node:fs/promises";
import { resolve, join } from "node:path";
import { homedir } from "node:os";
import { fileURLToPath } from "node:url";
import { createHash, randomUUID } from "node:crypto";
const bytes = (s) => Buffer.byteLength(s, "utf8");
export function loopbackEndpoint(value, provider) {
  const u = new URL(
    value ||
      (provider === "ollama"
        ? "http://127.0.0.1:11434/v1"
        : "http://127.0.0.1:1234/v1"),
  );
  if (u.hostname === "localhost") u.hostname = "127.0.0.1";
  if (
    !["127.0.0.1", "[::1]"].includes(u.hostname) ||
    u.protocol !== "http:" ||
    u.username ||
    u.password ||
    u.search ||
    u.hash ||
    !/^\/v1\/?$/.test(u.pathname)
  )
    throw Error(
      "Use a loopback HTTP /v1 endpoint. Remote servers, redirects and credentials in URLs are refused.",
    );
  u.pathname = "/v1/";
  return u;
}
function appOrigin(value, { test = false } = {}) {
  const u = new URL(value);
  if (
    u.username ||
    u.password ||
    u.search ||
    u.hash ||
    u.pathname !== "/" ||
    (u.protocol !== "https:" &&
      !(test && u.protocol === "http:" && u.hostname === "127.0.0.1"))
  )
    throw Error("Use the HTTPS origin of your TACITUS App.");
  return u.origin;
}
async function jsonFetch(
  url,
  { method = "GET", body, token, signal, maxBytes = 80000 } = {},
) {
  const r = await fetch(url, {
    method,
    redirect: "error",
    signal,
    headers: {
      Accept: "application/json",
      ...(body ? { "Content-Type": "application/json" } : {}),
      ...(token ? { Authorization: "Bearer " + token } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (!r.ok)
    throw Object.assign(
      Error("HTTP " + r.status + " from " + new URL(url).origin),
      { status: r.status },
    );
  const reader = r.body.getReader(),
    chunks = [];
  let n = 0;
  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      n += value.length;
      if (n > maxBytes)
        throw Error("Response exceeds the local companion bound.");
      chunks.push(value);
    }
  } finally {
    await reader.cancel().catch(() => {});
  }
  const data = Buffer.concat(chunks);
  return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(data));
}
export async function discoverModels({
  provider,
  endpoint,
  contextTokens = 8192,
}) {
  if (
    !["ollama", "lmstudio"].includes(provider) ||
    !Number.isSafeInteger(contextTokens) ||
    contextTokens < 2048 ||
    contextTokens > 1048576
  )
    throw Error("Choose ollama or lmstudio and a supported context window.");
  const base = loopbackEndpoint(endpoint, provider),
    origin = base.origin;
  if (provider === "ollama") {
    const data = await jsonFetch(origin + "/api/tags", {
        signal: AbortSignal.timeout(10000),
      }),
      models = [];
    for (const m of data.models || []) {
      if (models.length >= 12) break;
      const name = m.name ?? m.model;
      if (
        typeof name !== "string" ||
        bytes(name) > 200 ||
        m.remote_host ||
        m.remote_model ||
        m.cloud ||
        /[:_-]cloud(?:$|[:_-])/i.test(name)
      )
        continue;
      // /api/show is metadata-only: it neither downloads nor runs a model.
      const info = await jsonFetch(origin + "/api/show", {
        method: "POST",
        body: { model: name },
        signal: AbortSignal.timeout(10000),
      });
      if (
        info.remote_host ||
        info.remote_model ||
        info.cloud ||
        !info.model_info
      )
        continue;
      const declared = Object.entries(info.model_info).find(
        ([k, v]) => k.endsWith(".context_length") && Number.isSafeInteger(v),
      )?.[1];
      const window = Math.min(contextTokens, declared ?? contextTokens);
      if (window < 2048) continue;
      models.push({
        id: name,
        label: name,
        provider,
        context_tokens: window,
        max_output_tokens: Math.min(1024, Math.floor(window / 4)),
        identity:
          [m.digest, m.details?.quantization_level]
            .filter(Boolean)
            .join(" · ")
            .slice(0, 300) || "Local server model; identity not reported",
      });
    }
    if (!models.length)
      throw Error(
        "No installed local model was found. Install one yourself in Ollama, then try again.",
      );
    return models;
  }
  const data = await jsonFetch(new URL("models", base), {
    signal: AbortSignal.timeout(10000),
  });
  const models = (data.data || [])
    .filter(
      (m) =>
        typeof m.id === "string" && bytes(m.id) <= 200 && !/embed/i.test(m.id),
    )
    .slice(0, 12)
    .map((m) => ({
      id: m.id,
      label: m.id,
      provider,
      context_tokens: contextTokens,
      max_output_tokens: Math.min(1024, Math.floor(contextTokens / 4)),
      identity:
        "LM Studio local-server identifier; weights and placement are user-controlled",
    }));
  if (!models.length)
    throw Error(
      "No model is available from LM Studio. Load a model and start its local server.",
    );
  return models;
}
async function savePrivate(path, value) {
  const text = JSON.stringify(value, null, 2) + "\n",
    temp = path + "." + randomUUID() + ".tmp";
  await writeFile(temp, text, { mode: 0o600, flag: "wx" });
  await rename(temp, path);
}
export async function pair({
  app,
  code,
  provider,
  endpoint,
  stateDir,
  contextTokens = 8192,
  test = false,
}) {
  const origin = appOrigin(app, { test }),
    base = loopbackEndpoint(endpoint, provider),
    models = await discoverModels({
      provider,
      endpoint: base.href,
      contextTokens,
    });
  if (!/^tc_pair_[a-f0-9]{64}$/.test(code || ""))
    throw Error("Copy a current one-time pairing code from the App.");
  const connected = await jsonFetch(origin + "/api/local/v1/claim", {
    method: "POST",
    body: { pair_code: code, models },
    signal: AbortSignal.timeout(15000),
  });
  if (
    !/^tc_local_[a-f0-9]{64}$/.test(connected.token || "") ||
    !/^lc_[a-f0-9]+$/.test(connected.id || "")
  )
    throw Error("The App returned an invalid connection.");
  await mkdir(stateDir, { recursive: true, mode: 0o700 });
  await savePrivate(join(stateDir, "connection.json"), {
    app: origin,
    id: connected.id,
    token: connected.token,
    provider,
    endpoint: base.href,
    contextTokens,
    scope: connected.scope,
    paired_at: new Date().toISOString(),
  });
  return { id: connected.id, models: models.map((m) => m.id), stateDir };
}
export async function executeClaim({
  connection,
  claim,
  modelDirectory,
  stateDir,
  test = false,
}) {
  const origin = appOrigin(connection.app, { test }),
    base = loopbackEndpoint(connection.endpoint, connection.provider);
  const request = claim.request;
  if (
    claim.state !== "claimed" ||
    !/^lj_[a-f0-9]{64}$/.test(claim.id || "") ||
    request?.job_id !== claim.id ||
    !/^[a-f0-9]{64}$/.test(claim.request_sha256 || "") ||
    createHash("sha256").update(JSON.stringify(request)).digest("hex") !==
      claim.request_sha256
  )
    throw Error("The claimed request does not match its receipt.");
  if (
    request.schema !== "tacitus-local-model-request/1" ||
    request.provider !== connection.provider ||
    !modelDirectory.some((m) => m.id === request.model)
  )
    throw Error("The selected model is not in this paired local model list.");
  const config = request.request;
  if (
    Object.keys(config).some(
      (k) =>
        ![
          "model",
          "messages",
          "max_tokens",
          "temperature",
          "stream",
          "response_format",
        ].includes(k),
    ) ||
    config.model !== request.model ||
    !Array.isArray(config.messages) ||
    config.messages.some(
      (m) =>
        !["system", "user", "assistant"].includes(m.role) ||
        typeof m.content !== "string",
    ) ||
    config.tools ||
    config.functions ||
    config.stream !== false ||
    !Number.isSafeInteger(config.max_tokens) ||
    config.max_tokens > 4096 ||
    bytes(JSON.stringify(config)) > 64000
  )
    throw Error(
      "Unsupported model request. No tool or external action is permitted.",
    );
  const path = join(stateDir, claim.id + ".json");
  try {
    await readFile(path);
    throw Error(
      "This request was already claimed locally. Inspect its retained recording; inference is not repeated.",
    );
  } catch (e) {
    if (e.code !== "ENOENT") throw e;
  }
  await savePrivate(path, {
    state: "claimed",
    claim,
    started_at: new Date().toISOString(),
  });
  const controller = new AbortController(),
    started = Date.now();
  let timer, heartbeat;
  try {
    timer = setTimeout(
      () => controller.abort(),
      Math.min(300000, Math.max(1, Date.parse(claim.expires_at) - Date.now())),
    );
    heartbeat = setInterval(async () => {
      try {
        const state = await jsonFetch(
          origin + "/api/local/v1/jobs/" + claim.id + "/status",
          { token: connection.token, signal: AbortSignal.timeout(10000) },
        );
        if (!state.active) controller.abort();
      } catch {
        controller.abort();
      }
    }, 3000);
    let output;
    if (connection.provider === "ollama") {
      const model = modelDirectory.find((m) => m.id === request.model);
      const wire = {
        model: request.model,
        messages: config.messages,
        stream: false,
        think: false,
        format: config.response_format.json_schema.schema,
        options: {
          num_ctx: model.context_tokens,
          num_predict: config.max_tokens,
          temperature: config.temperature,
        },
      };
      const native = await jsonFetch(base.origin + "/api/chat", {
        method: "POST",
        body: wire,
        signal: controller.signal,
        maxBytes: 18000,
      });
      output = {
        model: native.model,
        choices: [
          {
            finish_reason:
              native.done === true
                ? (native.done_reason ?? "stop")
                : "incomplete",
            message: {
              content: native.message?.content,
              tool_calls: native.message?.tool_calls,
            },
          },
        ],
        usage: {
          prompt_tokens: native.prompt_eval_count,
          completion_tokens: native.eval_count,
        },
        tacitus_adapter: {
          id: "ollama-native-v1",
          wire_request_sha256: createHash("sha256")
            .update(JSON.stringify(wire))
            .digest("hex"),
        },
      };
    } else {
      output = await jsonFetch(new URL("chat/completions", base), {
        method: "POST",
        body: config,
        signal: controller.signal,
        maxBytes: 18000,
      });
      output.tacitus_adapter = {
        id: "lmstudio-openai-v1",
        wire_request_sha256: createHash("sha256")
          .update(JSON.stringify(config))
          .digest("hex"),
      };
    }
    const result = {
      request_sha256: claim.request_sha256,
      output,
      elapsed_ms: Date.now() - started,
    };
    await savePrivate(path, { state: "result_pending", claim, result });
    const accepted = await jsonFetch(
      origin + "/api/local/v1/jobs/" + claim.id + "/result",
      {
        method: "POST",
        body: result,
        token: connection.token,
        signal: AbortSignal.timeout(15000),
      },
    );
    await savePrivate(path, { state: "complete", claim, result, accepted });
    return { id: claim.id, state: "complete" };
  } catch (e) {
    let saved;
    try {
      saved = JSON.parse(await readFile(path, "utf8"));
    } catch {}
    if (saved?.state !== "result_pending")
      await savePrivate(path, {
        state: "uncertain",
        claim,
        error:
          "Local request interrupted or result unavailable. Inference will not be repeated automatically.",
      });
    throw e;
  } finally {
    clearTimeout(timer);
    clearInterval(heartbeat);
  }
}
export async function run({
  stateDir,
  once = false,
  test = false,
  onStatus = () => {},
}) {
  const connection = JSON.parse(
    await readFile(join(stateDir, "connection.json"), "utf8"),
  );
  appOrigin(connection.app, { test });
  loopbackEndpoint(connection.endpoint, connection.provider);
  const models = await discoverModels({
    provider: connection.provider,
    endpoint: connection.endpoint,
    contextTokens: connection.contextTokens,
  });
  await jsonFetch(connection.app + "/api/local/v1/models", {
    method: "POST",
    body: { models },
    token: connection.token,
    signal: AbortSignal.timeout(15000),
  });
  // Only delivery of a retained completed result is retried; inference is never replayed.
  for (const file of await readdir(stateDir))
    if (/^lj_[a-f0-9]{64}\.json$/.test(file)) {
      const path = join(stateDir, file),
        saved = JSON.parse(await readFile(path, "utf8"));
      if (saved.state === "result_pending") {
        const accepted = await jsonFetch(
          connection.app + "/api/local/v1/jobs/" + saved.claim.id + "/result",
          {
            method: "POST",
            body: saved.result,
            token: connection.token,
            signal: AbortSignal.timeout(15000),
          },
        );
        await savePrivate(path, { ...saved, state: "complete", accepted });
      }
    }
  do {
    const claim = await jsonFetch(connection.app + "/api/local/v1/jobs", {
      token: connection.token,
      signal: AbortSignal.timeout(15000),
    });
    if (claim.state === "claimed")
      onStatus(
        await executeClaim({
          connection,
          claim,
          modelDirectory: models,
          stateDir,
          test,
        }),
      );
    else onStatus({ state: claim.state });
    if (once) return;
    await new Promise((resolve) => setTimeout(resolve, 2500));
  } while (true);
}
async function cli() {
  const [command, ...args] = process.argv.slice(2),
    options = {};
  for (let i = 0; i < args.length; i += 2) {
    if (!args[i].startsWith("--") || !args[i + 1])
      throw Error("Use --option value pairs.");
    options[args[i].slice(2)] = args[i + 1];
  }
  const stateDir = resolve(
    options["state-dir"] || join(homedir(), ".config", "tacitus-local"),
  );
  if (command === "models") {
    const models = await discoverModels({
      provider: options.provider || "ollama",
      endpoint: options.endpoint,
      contextTokens: Number(options.context || 8192),
    });
    console.log(JSON.stringify(models, null, 2));
    return;
  }
  if (command === "pair") {
    const result = await pair({
      app: options.app || "https://app.tacitus.me/",
      code: options.code,
      provider: options.provider || "ollama",
      endpoint: options.endpoint,
      stateDir,
      contextTokens: Number(options.context || 8192),
    });
    console.log(
      "Paired " +
        result.id +
        ". " +
        result.models.length +
        " installed models are available. Token saved privately; no inference was performed.",
    );
    return;
  }
  if (command === "run") {
    await run({
      stateDir,
      once: options.once === "true",
      onStatus: (s) => console.log(s.id ? s.id + " " + s.state : s.state),
    });
    return;
  }
  console.log(
    "Node 24+ · TACITUS local companion\nmodels --provider ollama|lmstudio\npair --app https://app.tacitus.me/ --code PAIR_CODE --provider ollama|lmstudio\nrun\nOptional: --endpoint http://127.0.0.1:PORT/v1 --context TOKENS --state-dir DIRECTORY",
  );
}
if (
  process.argv[1] &&
  resolve(process.argv[1]) === fileURLToPath(import.meta.url)
)
  cli().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
