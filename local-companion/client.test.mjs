import test from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { mkdtemp, readFile, stat, rm } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { createHash } from "node:crypto";
import {
  loopbackEndpoint,
  discoverModels,
  pair,
  run,
  executeClaim,
} from "./client.mjs";
async function fixture(t) {
  let inference = 0,
    delivered = 0,
    next = null;
  const token = "tc_local_" + "a".repeat(64),
    code = "tc_pair_" + "b".repeat(64);
  const server = createServer(async (req, res) => {
    let body = "";
    for await (const c of req) body += c;
    const p = body ? JSON.parse(body) : null;
    res.setHeader("Content-Type", "application/json");
    let result;
    if (req.url === "/api/tags")
      result = {
        models: [
          {
            name: "local-test",
            digest: "synthetic-hash",
            details: { quantization_level: "synthetic" },
          },
          { name: "remote:cloud", remote_host: "remote.example" },
        ],
      };
    else if (req.url === "/api/show")
      result = { model_info: { "synthetic.context_length": 32768 } };
    else if (req.url === "/api/local/v1/claim") {
      assert.equal(p.pair_code, code);
      result = {
        id: "lc_123abc",
        token,
        scope: { kind: "profile", id: "synthetic" },
      };
    } else if (req.url === "/api/local/v1/models") {
      assert.equal(req.headers.authorization, "Bearer " + token);
      result = { models: p.models.length };
    } else if (req.url === "/api/local/v1/jobs") {
      result = next ?? { state: "idle" };
      next = null;
    } else if (req.url.endsWith("/status")) result = { active: true };
    else if (req.url.endsWith("/result")) {
      delivered++;
      assert.equal(req.headers.authorization, "Bearer " + token);
      assert.equal(p.output.model, "local-test");
      result = { state: "complete" };
    } else if (req.url === "/api/chat") {
      inference++;
      assert.equal(p.model, "local-test");
      assert.equal(p.options.num_ctx, 8192);
      result = {
        model: "local-test",
        done: true,
        done_reason: "stop",
        message: {
          content: '{"text":"Synthetic reply","questions":[],"analysis":[]}',
        },
        prompt_eval_count: 50,
        eval_count: 10,
      };
    } else {
      res.statusCode = 404;
      result = { error: "not_found" };
    }
    res.end(JSON.stringify(result));
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const origin = "http://127.0.0.1:" + server.address().port,
    stateDir = await mkdtemp(join(tmpdir(), "tacitus-local-test-"));
  t.after(async () => {
    await new Promise((r) => server.close(r));
    await rm(stateDir, { recursive: true, force: true });
  });
  return {
    origin,
    stateDir,
    code,
    get inference() {
      return inference;
    },
    get delivered() {
      return delivered;
    },
    queue(request) {
      const id = "lj_" + "c".repeat(64);
      const value = {
        schema: "tacitus-local-model-request/1",
        job_id: id,
        provider: "ollama",
        model: "local-test",
        request: {
          model: "local-test",
          messages: [
            { role: "system", content: "Synthetic fixture." },
            { role: "user", content: "Explain the selected context." },
          ],
          max_tokens: 1024,
          temperature: 0.1,
          stream: false,
          response_format: {
            type: "json_schema",
            json_schema: {
              name: "test",
              strict: true,
              schema: { type: "object" },
            },
          },
        },
        ...request,
      };
      next = {
        state: "claimed",
        id,
        request: value,
        request_sha256: createHash("sha256")
          .update(JSON.stringify(value))
          .digest("hex"),
        expires_at: new Date(Date.now() + 60000).toISOString(),
      };
      return next;
    },
  };
}
test("loopback inference endpoint validation refuses remote URLs, credentials and hidden parameters", () => {
  for (const value of [
    "https://remote.example/v1",
    "http://10.0.0.1/v1",
    "http://user:pass@127.0.0.1/v1",
    "http://127.0.0.1/v1?q=secret",
    "http://127.0.0.1/admin",
  ])
    assert.throws(() => loopbackEndpoint(value, "ollama"));
  assert.equal(
    loopbackEndpoint("http://localhost:11434/v1", "ollama").hostname,
    "127.0.0.1",
  );
});
test("discovery and pairing perform zero inference, exclude cloud models and save a private token", async (t) => {
  const f = await fixture(t),
    models = await discoverModels({
      provider: "ollama",
      endpoint: f.origin + "/v1",
    });
  assert.deepEqual(
    models.map((m) => m.id),
    ["local-test"],
  );
  await pair({
    app: f.origin + "/",
    code: f.code,
    provider: "ollama",
    endpoint: f.origin + "/v1",
    stateDir: f.stateDir,
    test: true,
  });
  assert.equal(f.inference, 0);
  assert.equal(
    (await stat(join(f.stateDir, "connection.json"))).mode & 0o777,
    0o600,
  );
});
test("a paired worker executes one pinned request and retains a result without repeating inference", async (t) => {
  const f = await fixture(t);
  await pair({
    app: f.origin + "/",
    code: f.code,
    provider: "ollama",
    endpoint: f.origin + "/v1",
    stateDir: f.stateDir,
    test: true,
  });
  const claim = f.queue();
  await run({ stateDir: f.stateDir, once: true, test: true });
  assert.equal(f.inference, 1);
  assert.equal(f.delivered, 1);
  const saved = JSON.parse(
    await readFile(join(f.stateDir, claim.id + ".json"), "utf8"),
  );
  assert.equal(saved.state, "complete");
  const connection = JSON.parse(
    await readFile(join(f.stateDir, "connection.json"), "utf8"),
  );
  await assert.rejects(
    executeClaim({
      connection,
      claim,
      modelDirectory: [{ id: "local-test" }],
      stateDir: f.stateDir,
      test: true,
    }),
    /already claimed/,
  );
  assert.equal(f.inference, 1);
});
test("unknown models and tool-bearing requests cannot reach the local model server", async (t) => {
  const f = await fixture(t);
  await pair({
    app: f.origin + "/",
    code: f.code,
    provider: "ollama",
    endpoint: f.origin + "/v1",
    stateDir: f.stateDir,
    test: true,
  });
  const connection = JSON.parse(
    await readFile(join(f.stateDir, "connection.json"), "utf8"),
  );
  await assert.rejects(
    executeClaim({
      connection,
      claim: f.queue({ model: "different" }),
      modelDirectory: [{ id: "local-test" }],
      stateDir: f.stateDir,
      test: true,
    }),
    /selected model/,
  );
  assert.equal(f.inference, 0);
  const claim = f.queue();
  claim.request.request.tools = [{ type: "function" }];
  claim.request_sha256 = createHash("sha256")
    .update(JSON.stringify(claim.request))
    .digest("hex");
  await assert.rejects(
    executeClaim({
      connection,
      claim,
      modelDirectory: [{ id: "local-test" }],
      stateDir: f.stateDir,
      test: true,
    }),
    /Unsupported model request/,
  );
  assert.equal(f.inference, 0);
});
